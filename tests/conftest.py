import json
from pathlib import Path

import pytest
import standard_morph
from aind_neuron_reconstruction_io.io import parse_json

from aind.nmcp.qc import process_qc

_PRE_REGISTRATION_SUITE = "default_pre_registration_tests"


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parent / "test_data"


@pytest.fixture
def small_reconstruction(test_data_dir):
    return json.loads((test_data_dir / "small_reconstruction.json").read_text())


@pytest.fixture
def full_reconstruction(test_data_dir):
    return json.loads((test_data_dir / "full_reconstruction.json").read_text())


@pytest.fixture
def small_rows(small_reconstruction):
    table = parse_json(small_reconstruction, False)[["node_id", "compartment", "x", "y", "z", "r", "parent"]]
    return [
        (int(node_id), int(compartment), float(x), float(y), float(z), float(r), int(parent))
        for node_id, compartment, x, y, z, r, parent in table.itertuples(index=False, name=None)
    ]


@pytest.fixture
def small_node_data(small_rows):
    keys = ("index", "structure", "x", "y", "z", "radius", "parentIndex")
    return [dict(zip(keys, row)) for row in small_rows]


@pytest.fixture
def small_swc_file(tmp_path, small_rows) -> Path:
    path = tmp_path / "small.swc"
    path.write_text("".join(" ".join(str(value) for value in row) + "\n" for row in small_rows))
    return path


@pytest.fixture
def suite_spy(monkeypatch):
    """Records each (context, suite_name) and always runs the pre-registration suite, so no atlas is loaded."""
    calls = []

    def spy(input_data, context, suite_name):
        calls.append((context, suite_name))
        return standard_morph.run_qc(input_data, context, suite_name=_PRE_REGISTRATION_SUITE)

    monkeypatch.setattr(process_qc, "run_qc", spy)
    return calls


def metric(document, name):
    return next(m for m in document["metrics"] if m["name"] == name)


def metric_status(document, name):
    return metric(document, name)["status_history"][-1]["status"]
