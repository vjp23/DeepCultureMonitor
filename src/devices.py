import time
import busio
import board
import statistics
from RPLCD.i2c import CharLCD
import adafruit_ads1x15.ads1015 as ADS
from atlas_i2c import sensors, commands
from w1thermsensor import W1ThermSensor
from adafruit_ads1x15.analog_in import AnalogIn
from w1thermsensor import W1ThermSensor
from gpiozero import RGBLED, Button, DigitalOutputDevice


class RGBLEDButton(object):

    def __init__(self, button_pin, button_func, red_pin, green_pin, blue_pin, cathode=False):
        self.led = RGBLED(red=red_pin,
                          green=green_pin,
                          blue=blue_pin,
                          active_high=cathode)
        self.button = Button(button_pin, bounce_time=0.1)
        self.button.when_pressed = button_func

    @staticmethod
    def _hextofloats(h):
        'Takes a hex rgb string (e.g. #ffffff) and returns an RGB tuple (float, float, float).'
        return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)) # skip '#'

    def color(self, hex_color=None, rgb_color=None):
        assert hex_color is not None or rgb_color is not None, 'No color passed!'
        
        if hex_color is not None:
            rgb_tupe = self._hextofloats(hex_color)
        else:
            rgb_tupe = rgb_color

        self.led.color = rgb_tupe

    def off(self):
        self.color(rgb_color=(0, 0, 0))


class LCD(object):

    def __init__(self):
        self.lcd = CharLCD(i2c_expander='MCP23008', address=0x20,
                           cols=16, rows=2, backlight_enabled=False)

    def write(self, msg, reset=True):
        if reset:
            self.lcd.clear()
        self.lcd.write_string(msg)
        self.on()

    def quick_write(self, msg, cursor_pos=(1,0)):
        self.lcd.cursor_pos = cursor_pos
        lcd.write_string(msg)

    def clear(self):
        self.lcd.clear()

    def on(self):
        self.lcd.backlight_enabled = True

    def off(self):
        self.lcd.backlight_enabled = False


class Solenoid(object):

    def __init__(self, pin):
        self.output = MOSFETSwitch(pin=pin)

    def open(self):
        self.output.on()

    def close(self):
        self.output.off()


class MOSFETSwitch(object):

    def __init__(self, pin):
        self.mosfet = DigitalOutputDevice(pin=pin,
                                          active_high=True,
                                          initial_value=False)

    def on(self):
        self.mosfet.on()

    def off(self):
        self.mosfet.off()


class AtlasSensor(object):

    def __init__(self, name, address, post_func=None, modality=-1):
        self.sensor = self._setup(name, address)
        self.name = name
        self.modality = modality
        self.post_func = post_func

    def _setup(self, name, address):
        sensor = sensors.Sensor(name, address)
        sensor.connect()
        return sensor

    def read(self, attempts=0):
        if attempts < 3:
            try:
                response = self.sensor.query(commands.READ)
                data = float(response.data)
                
                if self.post_func is not None:
                    data = self.post_func(data)

                return data

            except Exception as e:
                return self.read(attempts=attempts+1)

        raise SystemError(f'There is a problem communicating with the {self.name} sensor. {attempts} attempts failed.')


class WaterHeightSensor(object):

    def __init__(self, channel, mosfet_pin, slope=1, intercept=0, modality=-1):
        self.slope = slope
        self.intercept = intercept
        self.modality = modality

        # Use a MOSFET controller to turn the sensor voltage off between readings to avoid zapping the pH sensor
        self.mosfet = MOSFETSwitch(mosfet_pin)

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

    def _read_voltage(self, num_samples=9):
        self.mosfet.on()

        time.sleep(0.05)

        samples = []
        for _ in range(num_samples):
            samples.append(self.chan.voltage)

        self.mosfet.off()

        return statistics.median(samples)

    def _voltage_to_gallons(self, voltage):
        return round(max(self.slope * voltage + self.intercept, 0), 1)

    def read_voltage_gallons(self):
        return self.read(with_voltage=True)

    def read(self, with_voltage=False):
        voltage = self._read_voltage()
        gallons = self._voltage_to_gallons(voltage)
    
        if with_voltage:
            return gallons, voltage

        return gallons


class TempSensor(object):

    def __init__(self, modality=-1):
        self.sensor = W1ThermSensor()
        self.modality = modality

    def read(self, decimals=1):
        temp = self.sensor.get_temperature(W1ThermSensor.DEGREES_F)

        return round(temp, decimals)
