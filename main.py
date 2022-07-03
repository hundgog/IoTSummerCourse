from machine import Pin
from time import sleep
import dht

sensor = dht.DHT11(Pin(14))

import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient  # For use of MQTT protocol to talk to Adafruit IO
import ubinascii              # Needed to run any MicroPython code
import machine                # Interfaces with hardware components
import random

# BEGIN SETTINGS
# These need to be change to suit your environment
RANDOMS_INTERVAL = 10000 # milliseconds
last_random_sent_ticks = 0  # milliseconds

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "USERNAME"
AIO_KEY = "KEY"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_HUMIDITY_FEED = "YOURFEEDNAME"
AIO_TEMPERATURE_FEED = "YourSecondFeedName"

# FUNCTIONS

# Function to respond to messages from Adafruit IO
def sub_cb(topic, msg):          # sub_cb means "callback subroutine"
    print((topic, msg))          # Outputs the message that was received. Debugging use.

def send_random():
    global last_random_sent_ticks
    global RANDOMS_INTERVAL

    if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):
        return; # Too soon since last one sent.

    print("Publishing: {0} to {1} ... ".format(temp, AIO_TEMPERATURE_FEED), end='')
    print("Publishing: {0} to {1} ... ".format(hum, AIO_HUMIDITY_FEED), end='')
    try:
        client.publish(topic=AIO_TEMPERATURE_FEED, msg=str(temp))
        client.publish(topic=AIO_HUMIDITY_FEED, msg=str(hum))
        print("DONE")
    except Exception as e:
        print("FAILED")
    finally:
        last_random_sent_ticks = time.ticks_ms()


# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)

# Subscribed messages will be delivered to this callback
client.set_callback(sub_cb)
client.connect()
client.subscribe(AIO_TEMPERATURE_FEED)
print("Connected to %s, subscribed to %s topic" % (AIO_SERVER, AIO_TEMPERATURE_FEED))


try:                      # Code between try: and finally: may cause an error
                          # so ensure the client disconnects the server if
                          # that happens.
    while 1:
        sleep(2)
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print('Temperature: %3.1f C' %temp)
        print('Humidity: %3.1f %%' %hum)           # Repeat this loop forever
        client.check_msg()# Action a message if one is received. Non-blocking.
        send_random()     # Send a random number to Adafruit IO if it's time.
finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    print("Disconnected from Adafruit IO.")
