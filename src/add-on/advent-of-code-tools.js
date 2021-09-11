const HOST = 'localhost'
const PORT = 8000

const socket = new WebSocket(`ws://${HOST}:${PORT}${window.location.pathname}`);

socket.addEventListener('open', function (event) {
	socket.send('Connection Established');
});

socket.addEventListener('message', function (event) {
	console.log(event.data);
});
