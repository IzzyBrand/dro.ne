// function preload() {
//   a1 = loadImage("data/arm1.png");
//   a2 = loadImage("data/arm2.png");
//   a3 = loadImage("data/arm3.png");
//   a4 = loadImage("data/arm4.png");
// }


waitingPhrases = [
	"Coming soon...",
	"Launching soon...",
	"Tightening props...",
	"Charging batteries...",
	"Waking the hive mind...",	
	"Synchronizing the fleet...",
	"Strapping warm cookies to drone...",
	"Initiating launch sequence...",
	"flying 2 you soon...",
	"Thread-locking all the things...",
	"Flashing flight controllers..."
	]

waitingPhrase = waitingPhrases[0]

function setup() {
	createCanvas(windowWidth, windowHeight);
	textFont("Comfortaa");
	nameFontSize = windowWidth/20;
}



function draw() {
	background(255);
	textSize(nameFontSize);
	textW = textWidth(waitingPhrase);
  	text(waitingPhrase, (windowWidth - textW)/2, (windowHeight - nameFontSize)/2);
}

function changePhrase() {
	var newPhrase = waitingPhrases[Math.floor(Math.random() * (waitingPhrases.length-1))+1];
	waitingPhrase = newPhrase;
}


setInterval(changePhrase, 5000);
