import json
import sys

from aind.nmcp.qc.tools import process_file


def run_cli(monkeypatch, capsys, *args):
    monkeypatch.setattr(sys, "argv", ["nmcp-qc-process", *map(str, args)])
    process_file.main()
    return json.loads(capsys.readouterr().out)


def test_json_file_prints_json_envelope(monkeypatch, capsys, test_data_dir):
    body = run_cli(monkeypatch, capsys, test_data_dir / "small_reconstruction.json", "--id", "42")

    assert set(body) == {"serviceVersion", "standardMorphVersion", "reconstructionId", "qualityControl", "error"}
    assert body["reconstructionId"] == "42"
    assert body["error"] is None


def test_registered_flag(monkeypatch, capsys, test_data_dir, suite_spy):
    run_cli(monkeypatch, capsys, test_data_dir / "small_reconstruction.json", "--registered")

    assert [suite_name for _, suite_name in suite_spy] == ["default_post_registration_tests"]


def test_neuroglancer_flags(monkeypatch, capsys, test_data_dir):
    body = run_cli(monkeypatch, capsys, test_data_dir / "small_reconstruction.json", "--skeleton", "s3://x",
                   "--segments", "1", "2")

    assert all("segments=1,2" in m["reference"] for m in body["qualityControl"]["metrics"])


def test_missing_json_file_is_an_input_error(monkeypatch, capsys, tmp_path):
    body = run_cli(monkeypatch, capsys, tmp_path / "missing.json")

    assert body["error"]["stage"] == "input"
    assert body["qualityControl"] is None


def test_swc_file(monkeypatch, capsys, small_swc_file):
    body = run_cli(monkeypatch, capsys, small_swc_file)

    assert body["error"] is None
    assert len(body["qualityControl"]["metrics"]) > 0
