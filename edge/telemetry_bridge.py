"""
로봇 디바이스에서 MQTT로 들어오는 센서값을 수집해 /predict로 중계
실운영은 ROS2/Bridge 권장. 데모는 경량 MQTT 예시.
"""
import os, json, requests
from paho.mqtt import client as mqtt

BROKER = os.getenv("MQTT_BROKER","?")
TOPIC  = os.getenv("MQTT_TOPIC","robot/telemetry")
PREDICT = os.getenv("PREDICT_URL","http://robotics-model-route/predict")

def on_message(_c,_u,msg):
    try:
        payload = json.loads(msg.payload.decode())
        features = payload.get("features")
        r = requests.post(PREDICT, json={"features":features}, timeout=2)
        print("pred:", r.status_code, r.text[:80])
    except Exception as e:
        print("err:", e)

if __name__ == "__main__":
    cli = mqtt.Client()
    cli.connect(BROKER, 1883, 60)
    cli.subscribe(TOPIC)
    cli.on_message = on_message
    cli.loop_forever()
