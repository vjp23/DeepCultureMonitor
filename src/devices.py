import busio
import board
import digitalio
import statistics
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
import adafruit_ads1x15.ads1015 as ADS
from atlas_i2c import sensors, commands
from w1thermsensor import W1ThermSensor
from adafruit_ads1x15.analog_in import AnalogIn


GPIO.setmode(GPIO.BCM)


class PWMIO(object):
	def __init__(self, channel, freq=50, start=100, direction='out'):
		self.dir = direction
		self.channel = channel
		self.freq = freq

		_direction = GPIO.OUT if direction == 'out' else GPIO.IN
		GPIO.setup(channel, _direction)

		self.obj = GPIO.PWM(channel, self.freq)
		self.obj.start(start)

	def set_value(self, value):
		# Assume brightness in [0, 255]
		mod_value = int(round(100 - 100 * (value / 255)))
		self.obj.ChangeDutyCycle(mod_value)

	def stop(self, cleanup=True):
		self.obj.stop()
		if cleanup:
			GPIO.cleanup()


class WaterHeightSensor(object):

	def __init__(self, channel, slope, intercept):
		self.slope = slope
		self.intercept = intercept

		# Create the I2C bus
		i2c = busio.I2C(board.SCL, board.SDA)
		# Create the ADC object using the I2C bus
		ads = ADS.ADS1015(i2c)
		# Create single-ended input on channel
		if channel == 0:
			input_chan = ADS.P0
		elif channel == 1:
			input_chan = ADS.P1
		elif channel == 2:
			input_chan = ADS.P2
		elif channel == 3:
			input_chan = ADS.P3

		self.chan = AnalogIn(ads, input_chan)

	def read_voltage(self, num_samples=9):
		samples = []
		for _ in range(num_samples):
			samples.append(self.chan.voltage)

		return statistics.median(samples)

	def _voltage_to_gallons(self, voltage):
		return round(max(self.slope * voltage + self.intercept, 0), 1)


	def read(self):
		voltage = self.read_voltage()
		gallons = self._voltage_to_gallons(voltage)
		return gallons, voltage


class Solenoid(object):

	def __init__(self, channel):
		self.channel = channel
		GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)
		self.state = 0

	def open(self):
		if self.state == 0:
			GPIO.output(self.channel, GPIO.HIGH)
			self.state = 1

	def close(self):
		GPIO.output(self.channel, GPIO.LOW)
		self.state = 0


class AtlasSensor(object):

	def __init__(self, name, address):
		self.sensor = self._setup(name, address)

	def _setup(self, name, address):
		sensor = sensors.Sensor(name, address)
		sensor.connect()
		return sensor

	def read(self, attempts=0):
		if attempts < 3:
			try:
				response = self.sensor.query(commands.READ)
				return float(response.data)

			except Exception as e:
				return self.read(attempts=attempts+1)

		raise SystemError(f'There is a problem communicating with an Atlas sensor. {attempts} attempts failed.')