FROM arm32v6/python:3.9-rc-alpine

RUN apk add build-base

# Copy in the requirements.txt file
COPY build/requirements.txt .

RUN pip3 install --upgrade setuptools && \
	pip3 install -r requirements.txt 

ENV BUTTON_CHANNEL=4 \
    RED_LED_PIN=17 \
    GREEN_LED_PIN=27 \
    BLUE_LED_PIN=22 \
    SLND_PIN=21 \
    ETAPE_SWITCH_PIN=26 \
    ETAPE_CHANNEL=0 \
    RES_CAPACITY=6.5 \
    GAL_HEIGHT_SLOPE=4.83 \
    GAL_HEIGHT_INTERCEPT=-11.1 \
    SMS_NUM=+12345678910 \
    SMS_FLAG_PATH=/db/sms_flag.json \
    FILL_FLAG_PATH=/db/fill_flag.json \
    DB_NAME=/db/dwc-monitor-data.db \
    SAMPLE_INTERVAL=900

COPY src/ src/

WORKDIR src/

# Run the loop
ENTRYPOINT ["python3", "main.py"]
