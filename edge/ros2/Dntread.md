로컬 테스트
	•	터미널 1: ros2 run demo_nodes_cpp talker (확린용)
	•	터미널 2: python edge/ros2/telemetry_publisher.py
	•	터미널 3: python edge/ros2/telemetry_bridge.py
	•	model-server가 떠있다면 브리지가 /predict에 계속 샘플 POST 하면서 운영 루프가 살아있음을 보여준다.
