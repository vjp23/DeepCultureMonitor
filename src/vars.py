import os

BUTTON_PIN = int(os.environ['BUTTON_CHANNEL'])
RED_PIN = int(os.environ['RED_LED_PIN'])
GREEN_PIN = int(os.environ['GREEN_LED_PIN'])
BLUE_PIN = int(os.environ['BLUE_LED_PIN'])

SLND_PIN = int(os.environ['SLND_PIN'])
ETAPE_SWITCH_PIN = int(os.environ['ETAPE_SWITCH_PIN'])
ETAPE_CHANNEL = int(os.environ['ETAPE_CHANNEL'])

RES_CAPACITY = float(os.environ['RES_CAPACITY'])
V_TO_GAL_M = float(os.environ['GAL_HEIGHT_SLOPE'])
V_TO_GAL_B = float(os.environ['GAL_HEIGHT_INTERCEPT'])

SMS_NUM = os.environ['SMS_NUM']
SMS_FLAG = os.environt['SMS_FLAG_PATH']
DB_NAME = os.environ['DB_NAME']
FILL_FLAG = os.environ['FILL_FLAG_PATH']