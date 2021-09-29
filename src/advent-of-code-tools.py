#!/usr/bin/env python3

import argparse
import asyncio
import configparser
import glob
import logging
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime

import websockets
import websockets_routes


def start_server(host, port, config):
	"""
	Start die Advent of Code tools server. This is necessary for browser communication.

	:param host: Server host
	:param port: Server port
	:param config: Config from config file
	"""

	logging.basicConfig(level=logging.INFO)
	router = websockets_routes.Router()
	browser_sockets = defaultdict(dict)
	run_sockets = defaultdict(dict)

	@router.route('/{year}/day/{day}/output')
	async def handle_output(websocket, path):
		"""
		Handle output that should be submitted

		:param websocket:
		:param path:
		:return:
		"""

		data = await websocket.recv()
		run_sockets[path.params['year']][path.params['day']] = websocket
		logging.info(f'New client connection for {path.params["year"]}/{path.params["day"]}')
		await browser_sockets[path.params['year']][path.params['day']].send(data.rstrip('\n'))
		await websocket.wait_closed()

	@router.route('/{year}/day/{day}/answer')
	async def handle_answer(websocket, path):
		"""
		Handle answer

		:param websocket:
		:param path:
		:return:
		"""

		logging.info(f'Receiving answers for {path.params["year"]}/{path.params["day"]}')
		await run_sockets[path.params['year']][path.params['day']].send(await websocket.recv())
		await run_sockets[path.params['year']][path.params['day']].send(await websocket.recv())

	@router.route('/{year}/day/{day}')
	async def handle_input(websocket, path):
		"""
		Handle input and project creation.

		:param websocket:
		:param path:
		:return:
		"""

		year, day = path.params['year'], path.params['day']
		logging.info(f'New browser connection for {year}/{day}')
		browser_sockets[path.params['year']][path.params['day']] = websocket

		path = config['PATH_SOLUTION'].format(year=path.params['year'], day=path.params['day'], part=1)
		data = await websocket.recv()

		if not os.path.exists(path):
			logging.info(f'Copying template for {year}/{day}')
			shutil.copytree(config['PATH_TEMPLATE'], path)
			with open(f'{path}/{config["FILE_INPUT"]}', 'w') as f:
				f.write(data)

			os.makedirs(f'{path}/{config["PATH_EXAMPLES"]}', exist_ok=True)

		await websocket.wait_closed()
		logging.info(f'Closed connection for {year}/{day}')

	server = router.serve(host, port)
	asyncio.get_event_loop().run_until_complete(server)
	asyncio.get_event_loop().run_forever()


def run_solution(host, port, year, day, command, config, part=None):
	"""
	Run script which calculates solution.

	:param host: Server host
	:param port: Server port
	:param year: Exercise year
	:param day: Exercise day
	:param command: Command to execute
	:param config: Config from config file
	:param part: Part 1 or 2?
	:return:
	"""

	if part is None:
		if os.path.exists(config['PATH_SOLUTION'].format(year=year, day=day, part=2)):
			part = 2
		elif os.path.exists(config['PATH_SOLUTION'].format(year=year, day=day, part=1)):
			part = 1
		else:
			raise NotADirectoryError(
				f'No directory matching {config["PATH_SOLUTION"].format(year=year, day=day, part="[12]")}')

	path = config['PATH_SOLUTION'].format(year=year, day=day, part=part)
	if not os.path.exists(path):
		raise NotADirectoryError(f'No directory matching {path}')

	os.chdir(path)

	examples_path = f'{config["PATH_EXAMPLES"]}'

	def run_script(input_path, max_output_size=50):
		"""
		Run script as subprocess, stdout appears in console and will also be returned

		:param input_path: Input file for stdin
		:param max_output_size: Maximal possible length of the solution
		:return: stdout (including errors)
		"""

		process = subprocess.Popen(command, stdin=open(input_path), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		script_output = ''
		while process.poll() is None or process.stdout.peek():
			char = process.stdout.read(1).decode()
			script_output = (script_output + char)[-max_output_size:]
			print(char, end='')

		return script_output.rstrip('\n').split('\n')[-1]

	success = True  # main solution will only run if test cases passed
	for file in glob.glob(f'{examples_path}/*.in'):
		# empty input files should be ignored
		with open(file) as f:
			if f.read() == '':
				continue

		example_name = os.path.splitext(os.path.basename(file))[0]
		output_file = f'{examples_path}/{example_name}.out'

		if not os.path.exists(output_file):
			continue

		with open(output_file) as f:
			expected = f.read().rstrip('\n')
			if expected == '':
				continue

		print(f'---------- SOLUTION FOR {example_name} ----------')
		output = run_script(file)

		print()
		if expected == output:
			print('\x1b[32m', end='')
		else:
			success = False
			print('\x1b[31m', end='')

		print(f'Expected: {expected}')
		print(f'  Output: {output}\x1b[0m\n')

	if not success:
		return

	print('---------- FINAL SOLUTION ----------')
	time_start = datetime.now()
	solution = run_script(config["FILE_INPUT"])
	time_end = datetime.now()
	time_display = '{:.3f}s'.format((time_end - time_start).total_seconds())

	print(f'\nYour solution \x1b[2;3m({time_display})\x1b[0m:')
	print(f'\x1b[1m{solution}\x1b[0m')
	try:
		submit = input(f'Submit? (y/n): ')
	except KeyboardInterrupt:
		print()
		return

	if submit == 'y':
		async def upload(url):
			"""
			Upload solution to websocket URL. Receive server response.

			:param url: Websocket URL
			:return:
			"""

			async with websockets.connect(url) as websocket:
				await websocket.send(solution)
				return await websocket.recv() == '1', await websocket.recv()

		correct, answer = asyncio.run(upload(f'ws://{host}:{port}/{year}/day/{day}/output'))

		print(f'\n\x1b[2;3m[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]\x1b[0m')
		if correct:
			print('\x1b[32m', end='')

			if part == 1:
				shutil.copytree('.', '../part-2')
		else:
			print('\x1b[31m', end='')

		print(f'{answer}\x1b[0m\n')


if __name__ == '__main__':
	HOST = 'localhost'
	PORT = 8000

	parser = argparse.ArgumentParser(description='Advent of Code tools.')
	parser.add_argument('--host', default=HOST, help='Set server host')
	parser.add_argument('--port', default=PORT, type=int, help='Set server port')
	parser.add_argument('mode', choices=['server', 'run'],
						help='First start program with server, use run to run your solutions')
	parser.add_argument('path', help='Advent of Code Project path')

	if 'run' in sys.argv:
		parser.add_argument('year', type=int, help='Choose year (only for run mode)')
		parser.add_argument('day', type=int, help='Choose day (only for run mode)')
		parser.add_argument('--part', choices=[1, 2], type=int,
							help='Choose part, part 2 is preferred by default if it exists (only for run mode)')
		parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to run (only for run mode)')

	args = parser.parse_args()
	aoc_config = configparser.ConfigParser()
	aoc_config.read(f'{os.path.dirname(__file__)}/config')

	os.chdir(args.path)

	if args.mode == 'server':
		start_server(args.host, args.port, aoc_config['DEFAULT'])
	elif args.mode == 'run':
		try:
			run_solution(args.host, args.port, args.year, args.day, args.command, aoc_config['DEFAULT'], args.part)
		except NotADirectoryError as e:
			exit(e)
