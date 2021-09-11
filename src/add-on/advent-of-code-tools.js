const HOST = 'localhost'
const PORT = 8000

const socket = new WebSocket(`ws://${HOST}:${PORT}${window.location.pathname}`);

socket.addEventListener('open', function (event) {
	fetch(`${window.location.href}/input`)
		.then(response => response.text())
		.then(response => socket.send(response))
});

socket.addEventListener('message', function (event) {
	console.log(event.data);
});
