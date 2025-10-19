import requests
def test_predict():
    r = requests.post("http://localhost:8000/predict", json={"features":[1,2,3,4]})
    assert r.status_code == 200
    assert "probability" in r.json()
