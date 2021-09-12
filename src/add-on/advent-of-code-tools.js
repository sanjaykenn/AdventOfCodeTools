const HOST = 'localhost'
const PORT = 8000

const socket = new WebSocket(`ws://${HOST}:${PORT}${window.location.pathname}`);

/**
 * Fetching data from site. If adventofcode.com ever changes it's site causing incompatibilities with this add-on,
 * this is where to solve that issue.
 * @type {{getReturnLink: (function(): Element), getSubmitInput: (function(): Element), getAnswer: (function(): string), getSubmit: (function(): Element), getPart2Link: (function(): Element), isCorrect: (function(): boolean)}}
 */
const site = {
	/* Get submit input field */
	getSubmitInput: () => document.querySelector('input[name=answer]'),
	/* Get submit button */
	getSubmit: () => document.querySelector('input[type=submit][value="[Submit]"]'),
	/* Get answer of answer page button */
	getAnswer: () => document.querySelector('main').innerText,
	/* Check if answer is correct */
	isCorrect: () => site.getAnswer().startsWith("That's the right answer!"),
	/* Go pack to exercise if answer is incorrect */
	getReturnLink: () => document.querySelector('main article p a:last-child'),
	/* Go to part 2 if answer is correct */
	getPart2Link: () => document.querySelector('main article p a')
}

if (window.location.pathname.match('/\\d+/day/\\d+/answer')) {
	// handle answer page
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
	// upload input
	socket.addEventListener('open', function (event) {
		fetch(`${window.location.href}/input`)
			.then(response => response.text())
			.then(response => socket.send(response))
	});

	// submit solution
	socket.addEventListener('message', function (event) {
		site.getSubmitInput().value = event.data
		site.getSubmit().click()
	});
}