from time import time, strftime
from sms_utils import send_sms
from flag_utils import read_flag, set_flag
from devices import RGBLEDButton, LCD, Solenoid, AtlasSensor, WaterHeightSensor, TempSensor


class DWCController(object):

	def __init__(self, db, button_pin, rgb_pins, slnd_pin, height_chan, height_cal, 
				 res_cap, timeouts, colors, sms_num, fill_flag, sms_flag, verbose=True):
		self.state = 0
		self.fresh = False
		self.timeouts = timeouts
		self.colors = colors
		self.db = db
		self.sms_num = sms_num
		self.fill_flag = fill_flag
		self.sms_flag = sms_flag
		self.capacity = res_cap

		# Setup I/O devices
		self.button = RGBLEDButton(button_pin=button_pin,
								   button_func=self._button_callback,
								   red=rgb_pins[0],
								   green=rgb_pins[1],
								   blue=rgb_pins[2])
		self.lcd = LCD()
		self.solenoid = Solenoid(pin=slnd_pin)

		# Setup sensors
		self.etape = WaterHeightSensor(channel=height_chan,
									   slope=height_cal['m'],
									   intercept=height_cal['b'],
									   modality=0)
		self.ph = AtlasSensor(name='ph', 
							  address=99,
							  post_func = lambda x: round(x, 2),
							  modality=1)
		self.ec = AtlasSensor('ec', 
							  address=100,
							  post_func = lambda x: int(round(x / 2)),
							  modality=2)
		self.temp = TempSensor(modality=3)
		self.sensors = [self.etape, self.ph, self.ec, self.temp]

	def _loudspeaker(self, msg):
		if self.verbose:
			print(msg)

	def _button_callback(self):
		print('Button pushed')
		num_states = len(self.timeouts) + 1
		next_state = (self.state + 1) % num_states
		self.set_state(next_state)

	def _status_to_color(self):
		"""
		Eventually, implement a mapping of data values to color, allowing
		the RGB LED ring around the button to indicate system status.
		"""
		return (0.0625, 0.0, 1.0)

	def _timeout(self):
		self._loudspeaker('Timeout')
		self.set_state(0)

	def health_check(self):
		"""
		Eventually, implement the ability to set these alarm thresholds dynamically
		or with a config file or something.
		"""
		gal_lims = (5.5)
		temp_lims = (73)
		ph_lims = (5.6, 6.4)
		ec_lims = (400, 1500)

		gallons, temp, ph, ec = db.get_latest(modality=(0, 1, 2, 3))

		message = 'DWC system health alert:\n'
		alert = False

		if gallons < gal_lims[0]:
			alert = True
			message += '\nWater level low at ' + str(gallons) + ' gallons.'

		if temp > temp_lims[0]:
			alert = True
			message += '\nTemp high at ' + str(temp) ' degrees F.'

		if ph < ph_lims[0] or ph > ph_lims[1]:
			alert = True
			message += '\npH out of range at ' + str(ph) + '.'

		if ec < ec_lims[0] or ec > ec_lims[1]:
			alert = True
			message += '\nEC out of range at ' + str(ec) + ' PPM.\n'

		if alert:
			send_sms(message, self.sms_num)

	def _fill_tank(self):
		gallons = self.etape.read()

		while gallons < self.capacity:
			try:
				gallons = self.etape.read()
				self.solenoid.open()
				time.sleep(0.25)
			except Exception as e:
				send_sms(f'Error in DWC monitor while filling tank:\n\n{e}', self.sms_num, skip_validation=True)
				print(e)
		
		self.solenoid.close()

	def check_fill(self):
		fill_flag, _ = read_flag(self.fill_flag)

		if fill_flag == 1:
			send_sms('DWC filling tank...', self.sms_num, skip_validation=True)
			print('Fill flag set to 1. Filling tank at {}.'.format(strftime("%H:%M%p %Z on %b %d, %Y")))
			self._fill_tank()
			print('Tank fill completed at {}. Reset fill flag.'.format(strftime("%H:%M%p %Z on %b %d, %Y")))
			set_flag(self.fill_flag, 0)
			send_sms('DWC tank fill completed.', self.sms_num, skip_validation=True)
			print('Tank fill flag set to 0. Return to state one.')

	def check_state(self):
		if self.state > 0:
			max_state_time = self.timeouts[self.state - 1]
			now = time()
			if (now - self.state_start) >= max_state_time:
                self._timeout()
                return

		self.refresh()

	def set_state(self, state):
		self._loudspeaker('Setting state to ' + str(state))
		self.state = state
		self.fresh = True
		self.state_start = time()
		self.refresh()

	def refresh(self):
		if self.state == 0:
			if self.fresh:
				self.lcd.off()
				self.lcd.clear()
				self.fresh = False
			button_color = self._status_to_color()
			self.button.color(rgb_color=button_color)
		
		elif self.state == 1:
			self._state_one()
		
		elif self.state == 2:
			self._state_two()

	def _state_one(self):
		if self.fresh:
			self.button.color(hex_color=self.colors[0])
			gallons, temp, ph, ec = db.get_latest(modality=(0, 1, 2, 3))
			self.lcd.write('{gallons} gal, {}F\r\n{} pH, {} PPM'.format(gallons, 1, round(temp), round(ph, 2), ec), reset=True)
			self.fresh = False

	def _state_two(self):
		if self.fresh:
			self.button.color(hex_color=self.colors[1])
			gallons = db.get_latest(modality=(0))
			self.lcd.write('Gallons:', reset=True)
			self.fresh = False

		self.lcd.quick_write(msg='{}       '.format(round(gallons, 1)), 
						     cursor_pos=(1,0))
		time.sleep(0.25)
		

	def loop_iteration(self):
		if self.state == 0:
			# Check for a fill flag and fill the tank if requested
			self.check_fill()

			for sensor in self.sensors:
				# Read a sensor and write the data to the DB
				modality = sensor.modality
				data = sensor.read()
				timestamp = time()
				db.write_one(modality, data, timestamp)

			# Check health and sound alarm if necessary
			self.health_check()

		else:
			self.refresh()