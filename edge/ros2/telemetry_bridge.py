# /robot/telemetry_json 구독 → sensor_schema.json 검증 → /predict 로 전송
import os, json, requests, rclpy
from jsonschema import validate
from rclpy.node import Node
from std_msgs.msg import String

PREDICT_URL = os.getenv("PREDICT_URL", "http://robotics-model-route/predict")
SCHEMA_PATH = os.getenv("SCHEMA_PATH", "schemas/sensor_schema.json")

with open(SCHEMA_PATH, "r") as f:
    SCHEMA = json.load(f)

class TelemetryBridge(Node):
    def __init__(self):
        super().__init__('telemetry_bridge')
        self.sub = self.create_subscription(String, '/robot/telemetry_json', self.cb, 10)

    def cb(self, msg: String):
        try:
            payload = json.loads(msg.data)
            validate(payload, SCHEMA)
            r = requests.post(PREDICT_URL, json={"features": payload["features"]}, timeout=2)
            self.get_logger().info(f"predict {r.status_code} {r.text[:80]}")
        except Exception as e:
            self.get_logger().error(f"bridge error: {e}")

def main():
    rclpy.init()
    node = TelemetryBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
