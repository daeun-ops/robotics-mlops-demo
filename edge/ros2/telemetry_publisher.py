# rclpy 퍼블리셔: /robot/telemetry_json 에 JSON 문자열 발행
# 설치: sudo apt-get install ros-humble-desktop  (배포판에 맞게)
import json, os, time, random
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TelemetryPublisher(Node):
    def __init__(self):
        super().__init__('telemetry_publisher')
        self.pub = self.create_publisher(String, '/robot/telemetry_json', 10)
        self.robot_id = os.getenv("ROBOT_ID", "rbt-001")
        self.timer = self.create_timer(0.2, self.tick)

    def tick(self):
        msg = {
            "robot_id": self.robot_id,
            "ts": self.get_clock().now().to_msg().sec_nanosec()[0],
            # 데모: features 4개 (acc_mean, gyro_mean, wheel_vel, temp)
            "features": [round(random.uniform(-0.2,0.2),3), round(random.uniform(-0.2,0.2),3),
                         round(random.uniform(0.5,2.5),2), round(random.uniform(25.0,40.0),1)]
        }
        out = String()
        out.data = json.dumps(msg)
        self.pub.publish(out)

def main():
    rclpy.init()
    node = TelemetryPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
