import os

RED_PIN = int(os.environ['RED_LED_PIN'])
GREEN_PIN = int(os.environ['GREEN_LED_PIN'])
BLUE_PIN = int(os.environ['BLUE_LED_PIN'])
SLND_PIN = int(os.environ['SLND_PIN'])
ETAPE_CHANNEL = int(os.environ['ETAPE_CHANNEL'])

STATE_ONE_COLOR = os.environ['STATE_ONE_COLOR']
STATE_TWO_COLOR = os.environ['STATE_TWO_COLOR']
STATE_THREE_COLOR = os.environ['STATE_THREE_COLOR']

RES_CAPACITY = float(os.environ['RES_CAPACITY'])
V_TO_GAL_M = float(os.environ['GAL_HEIGHT_SLOPE'])
V_TO_GAL_B = float(os.environ['GAL_HEIGHT_INTERCEPT'])

STATE_TIMEOUT = float(os.environ['STATE_TIMEOUT'])
SMS_LEVEL = float(os.environ['SMS_LEVEL'])
	
DB_NAME = os.environ['DB_NAME']

FILL_FLAG = os.environ['FILL_FLAG_PATH']