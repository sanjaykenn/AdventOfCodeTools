import asyncio
import websockets

HOST = 'localhost'
PORT = 8000


async def handler(websocket, path):
	data = await websocket.recv()
	print(data, path)
	await websocket.send(data)


start_server = websockets.serve(handler, 'localhost', PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
