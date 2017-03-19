FROM hypriot/rpi-python:2.7.3
ADD *.py /
RUN apt-get update && apt-get install -y build-essential gcc python-dev python-pip python-smbus git
COPY Adafruit_Python_SHT31/Adafruit_SHT31.py /Adafruit_SHT31.py
COPY Adafruit_Python_DHT ./Adafruit_Python_DHT
COPY Adafruit_Python_GPIO ./Adafruit_Python_GPIO
RUN cd Adafruit_Python_DHT && \
    python setup.py install  && \
    cd ../Adafruit_Python_GPIO && \
    python setup.py install  && \
    cd /  && \
    pip install requests RPi.GPIO 
CMD [ "python", "/main.py" ]
