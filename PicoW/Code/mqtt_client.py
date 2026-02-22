from umqtt.simple import MQTTClient
from config import load_config

_client = None

def mqtt_connect():
    global _client
    cfg = load_config()

    if not cfg["mqtt"]["enabled"]:
        return

    try:
        _client = MQTTClient(
            cfg["mqtt"]["client_id"],
            cfg["mqtt"]["broker"],
            port=cfg["mqtt"]["port"]
        )
        _client.connect()
    except:
        _client = None

def mqtt_publish(payload):
    global _client
    if not _client:
        return

    try:
        topic = load_config()["mqtt"]["topic"]
        _client.publish(topic, payload)
    except:
        pass
