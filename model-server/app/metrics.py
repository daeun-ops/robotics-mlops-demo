"""
 Domain of robotics Operration difinition (Prometheus)
- API/performance: 요청수, 성공/실패수, 지연시간 히스토그램
- Model 품질 대리지표: 낮은 확신 비율, 입력 FPS, 드리프트(간단 KL)
- Domain 지표: 제어주기 지터, 안전정지 이벤트 수 등 (옵션)
"""
from prometheus_client import Counter, Histogram, Gauge

# API/performance (기본)
REQUESTS_TOTAL = Counter("inference_requests_total", "추론 요청 수", ["route"])
SUCCESS_TOTAL  = Counter("inference_success_total", "추론 성공 수", ["route"])
FAIL_TOTAL     = Counter("inference_failure_total", "추론 실패 수", ["route","reason"])
DURATION       = Histogram(
    "inference_duration_seconds",
    "추론 처리 시간(초)",
    buckets=(0.01,0.02,0.05,0.1,0.2,0.5,1,2,5)
)

# model 품질 대리 지표
LOWCONF_TOTAL  = Counter("inference_low_confidence_total", "낮은 확신(<=阈値) 추론 수")
CONFIDENCE_HIST= Histogram("inference_confidence", "추론 확률 분포", buckets=(0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0))
DRIFT_KL       = Gauge("input_kl_divergence", "입력 분포 KL Divergence (베이스라인 대비)")  # 주기적 계산

# input/pipeline 상태
INPUT_FPS      = Gauge("input_fps", "입력 프레임/샘플 처리 속도(FPS)")
QUEUE_BACKLOG  = Gauge("inference_queue_backlog", "대기 큐 길이(옵션)")

# robotices domain 지표 ( 로보트 만드는 사람이 요청하면 추가하는 식 / 난ㅁ
잘몰로
CONTROL_JITTER = Histogram("control_loop_jitter_seconds", "제어 루프 지터(초)", buckets=(0.001,0.005,0.01,0.02,0.05,0.1))
SAFETY_STOPS   = Counter("safety_stop_total", "안전 정지 발생 수", ["cause"])  # cause 예: e_stop, collision, anomaly
LOC_LOST_RATIO = Gauge("localization_lost_ratio", "SLAM Lost 비율(0~1)")
