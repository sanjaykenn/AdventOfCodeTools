#!/usr/bin/env python3

import argparse
import asyncio
import os
import re
import sys

import configparser
from distutils import dir_util

import websockets


def start_server(host, port, config):
	re_answer_path = re.compile('/(\\d+)/day/(\\d+)/answer')
	re_input_path = re.compile('/(\\d+)/day/(\\d+)')

	async def handler(websocket, path):
		m = re_answer_path.match(path)
		if m:
			pass
		else:
			m = re_input_path.match(path)
			if not m:
				return

			year, day = m.groups()
			path = config['PATH_SOLUTION'].format(year=year, day=day, part=1)
			data = await websocket.recv()

			if not os.path.exists(path):
				dir_util.copy_tree(config['PATH_TEMPLATE'], path)
				with open(f'{path}/{config["FILE_INPUT"]}', 'w') as f:
					f.write(data)

	server = websockets.serve(handler, host, port)
	asyncio.get_event_loop().run_until_complete(server)
	asyncio.get_event_loop().run_forever()


def run_solution(year, day, config, part=None):
	pass


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
		parser.add_argument('command', nargs='*', help='Command to run (only for run mode)')

	args = parser.parse_args()
	aoc_config = configparser.ConfigParser()
	aoc_config.read('config')

	os.chdir(args.path)

	if args.mode == 'server':
		start_server(args.host, args.port, aoc_config['DEFAULT'])
	elif args.mode == 'run':
		run_solution(args.year, args.day, aoc_config['DEFAULT'], args.part)
