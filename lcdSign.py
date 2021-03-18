# Simple LCD Message Sign Progarm
# Gets the weather, time, and custom messages from the user
# and displays them sequentially on the sign

# C Hyzer wrote this - 2/25/2020

from gpiozero import Button
import pickle
import datetime
import time
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
from yahoo_weather.weather import YahooWeather
from yahoo_weather.config.units import Unit

# Modify this if you have a different sized character LCD
lcd_columns = 20 
lcd_rows = 4

# Raspberry Pi Pin Config:
lcd_rs = digitalio.DigitalInOut(board.D26)  # pin 4
lcd_en = digitalio.DigitalInOut(board.D19)  # pin 6
lcd_d7 = digitalio.DigitalInOut(board.D27)  # pin 14
lcd_d6 = digitalio.DigitalInOut(board.D22)  # pin 13
lcd_d5 = digitalio.DigitalInOut(board.D24)  # pin 12
lcd_d4 = digitalio.DigitalInOut(board.D25)  # pin 11
lcd_backlight = digitalio.DigitalInOut(board.D4)

red = digitalio.DigitalInOut(board.D21)
green = digitalio.DigitalInOut(board.D12)
blue = digitalio.DigitalInOut(board.D18)

# Initialise the LCD class
lcd = characterlcd.Character_LCD_RGB(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns,
                                     lcd_rows, red, green, blue, lcd_backlight)
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 128, 255]

msgCount = 0
maxMessage = 4

lcd.clear()
lcd.color = GREEN

sleepTime = 5
msgFile = '/home/pi/sign/msgs.txt'

lastWeather = 0
weatherUpdateIntvl = 900 
msgArray = [None] * 24

# Pi feature button
button = Button(15)

data = YahooWeather(APP_ID="",
api_key="",
api_secret="")

# Comment out the data= lines above, the data.get_yahoo.. line below and uncomment the below
# to avoid hitting the Yahoo! API and use a pre-saved object w/ weather data.
#with open('data.pkl', 'rb') as input:
#        data = pickle.load(input)

def log(msg):
	now = datetime.datetime.now()
	print(now.strftime("%m/%d/%Y %H:%M:%S") + ': ' + msg)

# Weather update function
def updateWeather():
	
	global lastWeather
	global msgArray
	currtime = int(time.time())
	if currtime > (lastWeather + weatherUpdateIntvl):
		lcd.message = '\nUpdating Weather...'
		time.sleep(1)
		log('Getting weather...')
		data.get_yahoo_weather_by_city("Hartford, CT", Unit.fahrenheit)
		lastWeather = currtime
		msgArray[0] = 'Now in Berlin:\n' + data.condition.text + '\nTemperature: ' + str(data.condition.temperature) + 'F'

		for d in range (0, 3):
			msgArray[d+1] = 'Forecast on ' + data.forecasts[d].day + ':\n' + data.forecasts[d].text + '.\nHigh: ' + str(data.forecasts[d].high) + 'F, Low: ' + str(data.forecasts[d].low) + 'F'
		log('Done getting weather.')

# Update user-defined messages
def updateMessages():

	global msgArray	
	global maxMessage
	# Start at array index 4 (weather = 0-3, time/date = 4)
	d = 5 

	#print('Getting updated messages from ' + msgFile)
	with open(msgFile) as f:
		for line in f:
			msgArray[d] = parseMsg(line)
			maxMessage = d
			d += 1
	f.close()

# Parse the incoming message for the sign so text appears
# on the correct lines.
def parseMsg(message):
	# Find the last space, and trim the message if too long
	last = message.rfind(' ')
	if len(message) > 70:
		log('Message too long.  Trimmed to 70 characters.')
		message = message[:70]

	tmpMsg = ''
	index = 0

	# Break up the message using the last space before the 20th position.
	while index <= last:
		where = message.rfind(' ', index, index + 19)
		tmpMsg = tmpMsg + message[index:where] + '\n'
		index += where  + 1

	lastStr=tmpMsg[:-1]
	if len(lastStr) + len(message[last+1:len(message)]) > 19:
		tmpMsg = lastStr + '\n' + message[last+1:len(message)]
	else:
		tmpMsg = lastStr + message[last:len(message)]
	return tmpMsg

def setTime():
	now = datetime.datetime.now()
	tString= now.strftime("%I:%M %p")
	dString= now.strftime("%m/%d/%Y")
	msgArray[4] = 'Current Time & Date\n\n' + '     ' + dString + '\n      ' + tString

def wait():
	starttime = int(time.time())
	currtime = starttime
	while currtime < starttime + sleepTime:
		if button.is_pressed:
			time.sleep(.33)
			return
		currtime = int(time.time())
	time.sleep(.2)

log('Starting up...')

# Get the initial message list
updateWeather()
setTime()
updateMessages()

while True:

	# Get the updated weather and messages from file.
	lcd.clear()
	lcd.message = msgArray[msgCount]

	msgCount += 1
	# Update messages/weather after each cycle
	if msgCount > maxMessage:
		updateWeather()
		setTime()
		updateMessages()
		msgCount = 0

	# Sleep for 5 seconds - this will be replaced with a custom routine to allow
	# advancement with the button.
	#time.sleep(5)
	wait()

