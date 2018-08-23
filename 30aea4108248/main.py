#!/usr/bin/env python3
from umqtt.robust import MQTTClient
import network
import utime as time
import ubinascii
from machine import Pin, unique_id
import sensors
from config import config

sta_if = network.WLAN(network.STA_IF)

mqtt_host = config['mqtt']['host']
mqtt_username = config['mqtt']['username']
mqtt_password = config['mqtt']['password']

mcu_id = unique_id()
mcu_name = ubinascii.hexlify(mcu_id).decode('utf-8')

client = MQTTClient(mcu_name, mqtt_host, user=mqtt_username, password=mqtt_password)
client.connect()


def checkwifi():
    while not sta_if.isconnected():
        time.sleep_ms(500)
        print(".")
        sta_if.connect()


def is_mqtt_connected():
    try:
        client.ping()
    except OSError:
        print("Couldn't contact MQTT... trying again.")
        client.reconnect()


def main():
    #sensors.setup_pir_callback()
    noise_measurements = []
    while True:

        try:

            now = time.time()

            # Do the every second stuff
            #sensors.pir()
            noise = sensors.noise()
            noise_measurements.append(noise)

            # Do the 10 second stuff, which for me includes publishing mqtt messages
            if now % 10 == 0:

                noise_avg = sum(noise_measurements) / len(noise_measurements)

                # First check if wifi and MQTT is up
                checkwifi()
                is_mqtt_connected()

                # Now publish stats
                client.publish(b"home/kitchen/noise", str(noise_avg))

                # Reset
                noise_measurements = []

        except BaseException as error:
            print('An exception occurred: {}'.format(error))


if __name__ == '__main__':
    main()