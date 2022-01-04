import paho.mqtt.client as mqtt
import json
from lamp import Lamp

BASE_TOPIC = "lamp/cat"
STATE_TOPIC = f"{BASE_TOPIC}"
COMMAND_TOPIC = f"{BASE_TOPIC}/set"


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("lamp/cat/#")

def on_message(client, userdata, msg):

    if msg.topic == COMMAND_TOPIC:
        print(f"{msg.topic} {msg.payload.decode()}")
        client.lamp.read_json(msg.payload.decode())

        output = client.lamp.get_json().encode('utf-8')
        # print(f"payload in: {msg.payload}")
        # print(f"payload out: {output}")
        client.publish(STATE_TOPIC, payload=output)
    

    print(client.lamp)


def main():
    client = mqtt.Client()
    client.lamp = Lamp()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.1.7", 1883, 60)

    client.loop_forever()


if __name__ == "__main__":
    main()
