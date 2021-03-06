import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and

client = mqtt.Client()
client.on_connect = on_connect

try:
    client.connect("mqtt.eclipse.org", 1883, 5)
except:
    print("Could not connect to broker")
