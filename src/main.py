from vars import *
from controller import DWCController
from db_utils import DWCDatabaseHandler


db = DWCDatabaseHandler(DB_NAME)

controller = DWCController(db=db, 
                           button_pin=BUTTON_PIN, 
                           rgb_pins=(RED_PIN, GREEN_PIN, BLUE_PIN), 
                           slnd_pin=SLND_PIN, 
                           height_chan=ETAPE_CHANNEL,
                           height_pin=ETAPE_SWITCH_PIN,
                           height_cal={'m': V_TO_GAL_M, 'b': V_TO_GAL_B}, 
                           res_cap=RES_CAPACITY, 
                           timeouts=(30, 1200), 
                           colors=('#ff9100', '#009bdf'), 
                           sms_num=SMS_NUM, 
                           fill_flag=FILL_FLAG, 
                           sms_flag=SMS_FLAG,
                           interval=SAMPLE_INTERVAL,
                           verbose=True)

print('Controller setup. Begin loop iterations.')
try:
    while True:
        controller.loop_iteration()
finally:
    # Just to be safe, close the solenoid if something fails
    controller.solenoid.close()