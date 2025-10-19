from feast import Field, FeatureView, FileSource
from feast.types import Float32, Int64
source = FileSource(path="./data/features.parquet", timestamp_field="timestamp")
robot_features = FeatureView(
    name="robot_features",
    entities=["robot_id"],
    ttl=None,
    schema=[Field(name="acc_mean", dtype=Float32()), Field(name="gyro_mean", dtype=Float32())],
    source=source
)
