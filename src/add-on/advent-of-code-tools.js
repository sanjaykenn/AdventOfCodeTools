const HOST = 'localhost'
const PORT = 8000

const socket = new WebSocket(`ws://${HOST}:${PORT}${window.location.pathname}`);

const site = {
	getSubmitInput: () => document.querySelector('input[name=answer]'),
	getSubmit: () => document.querySelector('input[type=submit][value="[Submit]"]'),
	getAnswer: () => document.querySelector('main').innerText,
	isCorrect: () => site.getAnswer().startsWith("That's the right answer!"),
	getReturnLink: () => document.querySelector('main article p a:last-child'),
	getPart2Link: () => document.querySelector('main article p a')
}

if (window.location.pathname.match('/\\d+/day/\\d+/answer')) {
	socket.addEventListener('open', function (event) {
		if (site.isCorrect()) {
			socket.send('1')
			socket.send(site.getAnswer())
			site.getPart2Link().click()
		} else {
			socket.send('0')
			socket.send(site.getAnswer())
			site.getReturnLink().click()
		}
	});
} else if (window.location.pathname.match('/\\d+/day/\\d+')) {
	socket.addEventListener('open', function (event) {
		fetch(`${window.location.href}/input`)
			.then(response => response.text())
			.then(response => socket.send(response))
	});

	socket.addEventListener('message', function (event) {
		site.getSubmitInput().value = event.data
		site.getSubmit().click()
	});
}