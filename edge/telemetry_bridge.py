# edge/telemetry_bridge.py
# MQTT → /predict 브릿지 (장늠감)
import os, json, requests
from paho.mqtt import client as mqtt

BROKER = os.getenv("MQTT_BROKER","?")
TOPIC  = os.getenv("MQTT_TOPIC","robot/telemetry")
PREDICT= os.getenv("PREDICT_URL","http://robotics-model-route/predict")

def on_message(_c,_u,msg):
    try:
        payload = json.loads(msg.payload.decode())
        r = requests.post(PREDICT, json={"features": payload.get("features")}, timeout=2)
        print("pred:", r.status_code, r.text[:80])
    except Exception as e:
        print("err:", e)

if __name__ == "__main__":
    cli = mqtt.Client()
    cli.connect(BROKER, 1883, 60)
    cli.subscribe(TOPIC)
    cli.on_message = on_message
    cli.loop_forever()
