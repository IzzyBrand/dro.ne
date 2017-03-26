# Servo Control
import time
import wiringpi
 
# use 'GPIO naming'
wiringpi.wiringPiSetupGpio()
 
# set #18 to be a PWM output
wiringpi.pinMode(18, wiringpi.GPIO.PWM_OUTPUT)
 
# set the PWM mode to milliseconds stype
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
 
# divide down clock
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)
 
delay_period = 0.01
 
while True:
        for pulse in range(50, 250, 1):
                wiringpi.pwmWrite(18, pulse)
                time.sleep(delay_period)
        for pulse in range(250, 50, -1):
                wiringpi.pwmWrite(18, pulse)
                time.sleep(delay_period)

class Gripper:
	def __init__(self, pin):
		self.pin = pin
		# use 'GPIO naming'
		wiringpi.wiringPiSetupGpio()
		 
		# set #18 to be a PWM output
		wiringpi.pinMode(self.pin, wiringpi.GPIO.PWM_OUTPUT)
		 
		# set the PWM mode to milliseconds stype
		wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
		 
		# divide down clock
		wiringpi.pwmSetClock(192)
		wiringpi.pwmSetRange(2000)
		
		self.closed = False
		self.open()

	# open the gripper. Return True if an action took place
	def open(self):
		if self.closed:
			wiringpi.pwmWrite(self.pin, 200)
			self.closed = False
			return True
		else: return False

	# close the gripper. Return true if an action took place
	def close(self):
		if self.closed:
			return False
		else: 
			wiringpi.pwmWrite(self.pin, 100)
			self.closed = True
			return True

	# toggle the position of the gripper. Return if true if the gripper is now closed
	def toggle(self):
		if not self.open(): self.close()
		return self.closed