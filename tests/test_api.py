import pytest
from fastapi.testclient import TestClient

from aind.nmcp.qc.main import app
from conftest import metric_status

ENVELOPE_KEYS = {"serviceVersion", "standardMorphVersion", "reconstructionId", "qualityControl", "error"}


@pytest.fixture
def client():
    return TestClient(app)


def test_default_request(client, small_node_data):
    response = client.post("/performqc/", json={"id": "123", "data": small_node_data})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == ENVELOPE_KEYS
    assert body["reconstructionId"] == "123"
    assert body["error"] is None
    assert "object_type" in body["qualityControl"]


@pytest.mark.parametrize(
    ("extra", "suite_name"),
    [({}, "default_pre_registration_tests"), ({"isRegistered": True}, "default_post_registration_tests")],
)
def test_registration_selects_suite(client, small_node_data, suite_spy, extra, suite_name):
    response = client.post("/performqc/", json={"id": "1", "data": small_node_data, **extra})

    assert response.status_code == 200
    assert [recorded_suite for _, recorded_suite in suite_spy] == [suite_name]


def test_neuroglancer_options(client, small_node_data):
    body = {"id": "1", "data": small_node_data, "skeletonSource": "s3://skeletons", "segmentIds": [7]}

    response = client.post("/performqc/", json=body)

    references = [m["reference"] for m in response.json()["qualityControl"]["metrics"]]
    assert all("skeleton=s3://skeletons" in r and "segments=7" in r for r in references)


def test_missing_parent_index_is_rejected_by_validation(client, small_node_data):
    node = dict(small_node_data[0])
    del node["parentIndex"]

    response = client.post("/performqc/", json={"id": "1", "data": [node]})

    assert response.status_code == 422


def test_empty_data_is_a_finding(client):
    response = client.post("/performqc/", json={"id": "1", "data": []})

    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    assert metric_status(body["qualityControl"], "non_empty") == "Fail"
