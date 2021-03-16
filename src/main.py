import time
from db_utils import DWCDatabaseHandler
from flag_utils import read_flag, set_flag
from sms_utils import send_sms, reset_sms_status
from vars import *
from devices import *


def _get_data(temp_sensor, water_level_sensor, ph_sensor, ec_sensor, attempts=0, just_gallons=False, skip_sms=False):
	gallons, voltage = water_level_sensor.read()

	if gallons >= SMS_LEVEL: 
		if not skip_sms:
			response = send_sms(f'Low DWC water level warning!\n\nAdd {gallons} gallons as soon as possible.')
			if response is not None:
				if response != -1:
					print(f'Send SMS for low water level warning. Water below nominal level by {gallons} gallons.')
			else:
				print('Send failed.')
			
	else:
		reset_sms_status()
	
	if just_gallons:
		return gallons

	try:	
		temp = temp_sensor.get_temperature(W1ThermSensor.DEGREES_F)
	except IndexError:
		# Handle known hardware issue (likely a result of too-long leads)
		time.sleep(0.25)
		if attempts < 5:
			return _get_data(temp_sensor, water_level_sensor, ph_sensor, ec_sensor, attempts+1, just_gallons=False)
		else:
			raise SystemError(f'There is a problem communicating with the W1ThermSensor sensor. {attempts} attempts failed.')

	ph = round(ph_sensor.read(), 2)
	ec = int(round(ec_sensor.read() / 2))

	DB.write_all_to_db(voltage, gallons, temp, ph, ec)

	return gallons, round(temp, 1), ph, ec

	
def _hextofloats(h):
	'''Takes a hex rgb string (e.g. #ffffff) and returns an RGB tuple (float, float, float).'''
	return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) # skip '#'


def fill_tank(solenoid, water_level_sensor):
	gallons, _ = water_level_sensor.read()

	while gallons > 0:
		try:
			gallons, _ = water_level_sensor.read()
			solenoid.open()
			time.sleep(0.25)
		except Exception as e:
			send_sms(f'Error in DWC monitor while filling tank:\n\n{e}', skip_validation=True)
			print(e)
	
	solenoid.close()


def led_color(hex_color, red, green, blue):
	rgb = _hextofloats(hex_color)
	for led, value in zip([red, green, blue], rgb):
		led.set_value(value)


def lcd_msg(msg, lcd, reset=True):
	if reset:
		lcd.clear()
	lcd.backlight_enabled = True
	lcd.write_string(msg)


def still_fresh(on_at):
	return time.time() - on_at < STATE_TIMEOUT


def state_one(temp, water_level, lcd, red, green, blue, ph, ec):
	# Turn off the LCD screen and set the button color to green
	lcd.backlight_enabled = False
	lcd.clear()

	led_color(STATE_ONE_COLOR, red, green, blue)

	_, _, _, _ = _get_data(temp, water_level, ph, ec)


def state_two(temp, water_level, lcd, red, green, blue, reset, ph, ec):
	led_color(STATE_TWO_COLOR, red, green, blue)

	gallons, temp, phval, ppm = _get_data(temp, water_level, ph, ec)

	lcd_msg(f'Gallons low: {gallons}\r\nTemp:        {round(temp)}F', lcd, reset)
	lcd_msg(f'{RES_CAPACITY - gallons} gal, {round(temp)}F\r\n{phval} pH, {ppm} PPM', lcd, reset)

	time.sleep(0.5)


def state_three(water_level, lcd, button, red, green, blue, ph, ec):
	led_color(STATE_THREE_COLOR, red, green, blue)

	gallons = _get_data(None, water_level, ph, ec, just_gallons=True, skip_sms=True)
	lcd_msg('Gallons to add:', lcd, reset=True)

	time.sleep(0.5)

	while button.value:
		gallons = _get_data(None, water_level, ph, ec, just_gallons=True, skip_sms=True)

		lcd.cursor_pos = (1, 0)
		lcd.write_string(f'{round(gallons, 2)}     ')
		time.sleep(0.25)


try:
	DB = DWCDatabaseHandler(DB_NAME)
	print(f'Database setup using {DB_NAME}.')

	# Setup RGB LED ring around button
	RED = PWMIO(RED_PIN)
	GREEN = PWMIO(GREEN_PIN)
	BLUE = PWMIO(BLUE_PIN)
	print('RGB LEDs setup.')

	# Setup LCD screen, address is 0x20
	lcd = CharLCD(i2c_expander='MCP23008', address=0x20,
              cols=16, rows=2, backlight_enabled=False)
	print('LCD setup.')
	
	# Setup push button
	button = digitalio.DigitalInOut(board.D4)
	button.direction = digitalio.Direction.INPUT
	button.pull = digitalio.Pull.UP
	print('Button setup.')

	# Setup temp sensor
	temp = W1ThermSensor()
	print('Temp sensor setup.')

	# Setup water level ultrasonic ranger
	water_level = WaterHeightSensor(ETAPE_CHANNEL, V_TO_GAL_M, V_TO_GAL_B)
	print('E-Tape sensor setup.')

	# Setup pH sensor
	ph = AtlasSensor('ph', 99)
	print('pH sensor setup.')

	# Setup EC sensor
	ec = AtlasSensor('EC', 100)
	print('EC sensor setup.')

	# Setup the solenoid, controlled by MOSFET via digital GPIO pin
	solenoid = Solenoid(channel=SLND_PIN)
	print('Solenoid setup.')

	# Reset tank fill flag
	set_flag(FILL_FLAG, 0)
	print('Tank fill flag set to 0.')

	# Reset SMS send status
	reset_sms_status()
	print('SMS status reset.')

	on_since = 0

	# Start out in state one
	state_one(temp, water_level, lcd, RED, GREEN, BLUE, ph, ec)

	print('Ready!')

	while True:
		if not button.value:
			print(f'Button pushed- enter state two at {time.strftime("%H:%M%p %Z on %b %d, %Y")}')
			state_two(temp, water_level, lcd, RED, GREEN, BLUE, True, ph, ec)

			time.sleep(0.5)

			on_since = time.time()

			while still_fresh(on_since):
				if not button.value:
					print(f'Button pushed- enter state three at {time.strftime("%H:%M%p %Z on %b %d, %Y")}')
					state_three(water_level, lcd, button, RED, GREEN, BLUE, ph, ec)
					break

			print(f'Return to state one at {time.strftime("%H:%M%p %Z on %b %d, %Y")}')
			# Upon exiting state 2 or 3, return to state 1
			state_one(temp, water_level, lcd, RED, GREEN, BLUE, ph, ec)

			time.sleep(0.5)

		_, _, _, _ = _get_data(temp, water_level, ph, ec)

		fill_flag, _ = read_flag(FILL_FLAG)
		if fill_flag == 1:
			send_sms('DWC filling tank...', skip_validation=True)
			print(f'Fill flag set to 1. Filling tank at {time.strftime("%H:%M%p %Z on %b %d, %Y")}.')
			fill_tank(solenoid, water_level)
			print(f'Tank fill completed at {time.strftime("%H:%M%p %Z on %b %d, %Y")}. Reset fill flag.')
			set_flag(FILL_FLAG, 0)
			send_sms('DWC tank fill completed.', skip_validation=True)
			print('Tank fill flag set to 0. Return to state one.')

			
except Exception as e:
	solenoid.close()
	send_sms(f'Error in DWC monitor:\n\n{e}')
	print(e)

finally:
	solenoid.close()
	DB.close()
	lcd.backlight_enabled = False
	lcd.close(clear=True)
	RED.stop(cleanup=False)
	GREEN.stop(cleanup=False)
	BLUE.stop(cleanup=True)
