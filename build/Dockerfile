FROM arm32v6/python:3.9-rc-alpine

RUN apk add build-base

# Copy in the requirements.txt file
COPY build/requirements.txt .

RUN pip3 install --upgrade setuptools && \
	pip3 install -r requirements.txt 

# Set input pins et al- pin 4 is always the RGB LED button
ENV ETAPE_CHANNEL=0 \
    RED_LED_PIN=17 \
    GREEN_LED_PIN=27 \
    BLUE_LED_PIN=22 \
    SLND_PIN=21 \
    RES_CAPACITY=6 \
    GAL_HEIGHT_SLOPE=-6.7971 \
    GAL_HEIGHT_INTERCEPT=16.9465 \
    STATE_ONE_COLOR=#00ff74 \
    STATE_TWO_COLOR=#ff4ff3 \
    STATE_THREE_COLOR=#009bdf \
    STATE_TIMEOUT=15 \
    DB_NAME=/db/dwc-monitor-data.db \
    FILL_FLAG_PATH=/db/fill_flag.json \
    SMS_LEVEL=0.5

COPY src/ src/

WORKDIR src/

# Run the loop
ENTRYPOINT ["python3", "main.py"]
