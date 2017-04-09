function preload() {
  // a1 = loadImage("data/arm1.png");
  // a2 = loadImage("data/arm2.png");
  // a3 = loadImage("data/arm3.png");
  // a4 = loadImage("data/arm4.png");
}


waitingPhrases = [
	"Coming soon...",
	"Launching soon...",
	"Tightening props...",
	"Charging batteries...",
	"Waking the hive mind...",	
	"Synchronizing the fleet...",
	"Strapping cookies to drone...",
	"Initiating launch sequence...",
	"flying 2 you soon...",
	"Calibrating ESCs...",
	"Flashing flight controllers..."
	]

waitingPhrase = waitingPhrases[0]
armCornerRatio = 12.5/115.533;
var ang = 0

function setup() {
	createCanvas(windowWidth, windowHeight);
	textFont("Comfortaa");
	nameFontSize = windowWidth/25;
	rectMode(CENTER);
	imageMode(CENTER);
	textFont("Comfortaa");
}


function draw() {
	background(255);
	translate(windowWidth/2, windowHeight/2);
	// translate(0, windowHeight/3);
	textSize(nameFontSize);
	textW = textWidth(waitingPhrase);
  	text(waitingPhrase, - textW/2, - nameFontSize/2);
  	// translate(0, -windowHeight/2.5);
  	// if (ang >= 180) {
  	// 	ang = 0
  	// }
  	// if (ang < 90) { 
	  // 	drawLogo(ang * 0, ang * 1, ang * 2, ang * 3, windowHeight/4);
	  // 	ang++
  	// } else {
  	// 	drawLogo(ang * 4, ang * 3 - 180, ang * 2, ang * 1 - 180, windowHeight/4);
	  // 	ang++
  	// }
}

// function drawLogo(ang1,ang2,ang3,ang4,armSize) {
// 	console.log('Trying')
// 	rotate(ang1/180.0*PI);
//   	translate(armSize/2 - armSize * armCornerRatio, - armSize/2 + armSize * armCornerRatio);
//  	image(a1, 0, 0, armSize, armSize);
//  	// fill(255,0,0);
//  	// rect(0,0,armSize, armSize)
//   	translate(- armSize/2 + armSize * armCornerRatio, armSize/2 - armSize * armCornerRatio);
//  	rotate(- ang1/180.0*PI);
// 	rotate(ang2/180.0*PI);
//   	translate(armSize/2 - armSize * armCornerRatio, - armSize/2 + armSize * armCornerRatio);
//  	image(a2, 0, 0, armSize, armSize);
//  	// fill(0,255,0);
//  	// rect(0,0,armSize, armSize)
//   	translate(- armSize/2 + armSize * armCornerRatio, armSize/2 - armSize * armCornerRatio);
//  	rotate(- ang2/180.0*PI);
// 	rotate(ang3/180.0*PI);
//   	translate(armSize/2 - armSize * armCornerRatio, - armSize/2 + armSize * armCornerRatio);
//  	image(a3, 0, 0, armSize, armSize);
//  	// fill(0,0,255);
//  	// rect(0,0,armSize, armSize)
//   	translate(- armSize/2 + armSize * armCornerRatio, armSize/2 - armSize * armCornerRatio);
//  	rotate(- ang3/180.0*PI);
// 	rotate(ang4/180.0*PI);
//   	translate(armSize/2 - armSize * armCornerRatio, - armSize/2 + armSize * armCornerRatio);
//  	image(a4, 0, 0, armSize, armSize);
//  	// fill(200,0,200);
//  	// rect(0,0,armSize, armSize)
//   	translate(- armSize/2 + armSize * armCornerRatio, armSize/2 - armSize * armCornerRatio);
//  	rotate(- ang4/180.0*PI);
// }

function changePhrase() {
	var newPhrase = waitingPhrases[Math.floor(Math.random() * (waitingPhrases.length-1))+1];
	waitingPhrase = newPhrase;
}


setInterval(changePhrase, 5000);
