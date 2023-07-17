from gpiozero import DigitalOutputDevice
import time

pump1 = DigitalOutputDevice(16)
pump2 = DigitalOutputDevice(12)
pump3 = DigitalOutputDevice(26)
pump4 = DigitalOutputDevice(13)
pump5 = DigitalOutputDevice(6)

# Setup
pumps = [pump1, pump2, pump3, pump4, pump5]


def go(pump, go_for):
	try:
		pump.on()
		time.sleep(go_for)
	finally:
		pump.off()


def prime(pumps):
	for pump in pumps:
		go(pump, 5)


def dose(pump, mL, ml_per_minute=56.6):
	go_for = 60 * mL / ml_per_minute
	go(pump, go_for)
