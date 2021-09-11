#!/usr/bin/env python3

import argparse
import asyncio
import os
import sys

import websockets


def start_server(host, port):
	async def handler(websocket, path):
		data = await websocket.recv()
		print(data, path)
		await websocket.send(data)

	server = websockets.serve(handler, host, port)
	asyncio.get_event_loop().run_until_complete(server)
	asyncio.get_event_loop().run_forever()


def run_solution(year, day, part=None):
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
	os.chdir(args.path)

	if args.mode == 'server':
		start_server(args.host, args.port)
	elif args.mode == 'run':
		run_solution(args.year, args.day, args.part)
