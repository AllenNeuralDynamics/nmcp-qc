import dataclasses
import importlib.metadata

import pytest
import standard_morph
from standard_morph import Space

from aind.nmcp.qc import process_qc
from aind.nmcp.qc.process_qc import process_json, process_json_file, process_node_data, process_swc_file
from aind.nmcp.qc.quality_control_output import QualityControlOutput, ServiceError
from aind.nmcp.qc.reconstruction_input import NodeData, QualityControlOptions
from conftest import metric, metric_status

PARENT_NODE_DESCRIPTION = "The reconstruction may reference parent nodes that are not present in the file."
GENERIC_INPUT_DESCRIPTION = "An unexpected error occurred parsing the reconstruction data."


def node(index, structure, parent_index):
    return NodeData(index=index, structure=structure, x=float(index), y=float(index), z=float(index), radius=1.0,
                    parentIndex=parent_index)


def document_of(output: QualityControlOutput) -> dict:
    assert output.quality_control is not None
    return output.quality_control


def error_of(output: QualityControlOutput) -> ServiceError:
    assert output.error is not None
    return output.error


def test_default_run_returns_document(small_reconstruction):
    output = process_json("123", small_reconstruction)

    assert output.error is None
    assert output.reconstruction_id == "123"
    document = document_of(output)
    assert document["object_type"] == "Quality control"
    assert len(document["metrics"]) > 0
    assert all(m["tags"]["phase"] in {"integrity", "morphology"} for m in document["metrics"])
    assert all(m["name"] != "soma_inside_ccf_mesh" for m in document["metrics"])
    assert output.standard_morph_version == importlib.metadata.version("standard-morph")
    assert output.service_version == importlib.metadata.version("nmcpqc")


@pytest.mark.parametrize(
    ("is_registered", "space", "suite_name"),
    [
        (False, Space.IMAGE_SPACE, "default_pre_registration_tests"),
        (True, Space.CCF_REGISTERED, "default_post_registration_tests"),
    ],
)
def test_registration_selects_space_and_suite(small_reconstruction, suite_spy, is_registered, space, suite_name):
    output = process_json("1", small_reconstruction, QualityControlOptions(is_registered=is_registered))

    assert output.error is None
    [(context, recorded_suite)] = suite_spy
    assert context.space == space
    assert recorded_suite == suite_name


def test_default_runs_in_image_space(small_reconstruction, suite_spy):
    process_json("1", small_reconstruction)

    [(context, recorded_suite)] = suite_spy
    assert context.space == Space.IMAGE_SPACE
    assert recorded_suite == "default_pre_registration_tests"


def test_dangling_parent_is_a_finding_not_an_error():
    output = process_node_data("1", [node(1, 1, -1), node(2, 2, 99)])

    assert output.error is None
    assert metric_status(output.quality_control, "valid_parent_references") == "Fail"


def test_empty_node_data_is_a_finding_not_an_error():
    output = process_node_data("1", [])

    assert output.error is None
    document = document_of(output)
    assert metric_status(document, "non_empty") == "Fail"
    morphology = [m for m in document["metrics"] if m["tags"]["phase"] == "morphology"]
    assert morphology
    assert all(m["status_history"][-1]["status"] == "Pending" for m in morphology)


def test_large_input_serializes(full_reconstruction):
    output = process_json("1", full_reconstruction)

    assert output.error is None
    assert output.quality_control is not None


@pytest.mark.parametrize("as_str", [False, True], ids=["path", "str"])
def test_swc_path(small_swc_file, as_str):
    path = str(small_swc_file) if as_str else small_swc_file

    output = process_swc_file("1", path)

    assert output.error is None
    assert len(document_of(output)["metrics"]) > 0


@pytest.mark.parametrize(
    ("contents", "kind", "description"),
    [({}, "KeyError", PARENT_NODE_DESCRIPTION), ({"neurons": []}, "IndexError", GENERIC_INPUT_DESCRIPTION)],
)
def test_input_stage_errors(contents, kind, description):
    output = process_json("1", contents)

    assert error_of(output).stage == "input"
    assert error_of(output).kind == kind
    assert error_of(output).description == description
    assert output.quality_control is None
    assert output.service_version == importlib.metadata.version("nmcpqc")
    assert output.standard_morph_version == importlib.metadata.version("standard-morph")


def test_json_file_missing(tmp_path):
    output = process_json_file("1", tmp_path / "missing.json")

    assert error_of(output).stage == "input"
    assert error_of(output).kind == "FileNotFoundError"
    assert output.quality_control is None


def test_json_file_not_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json")

    output = process_json_file("1", path)

    assert error_of(output).stage == "input"
    assert error_of(output).kind == "JSONDecodeError"


def test_standard_morph_stage_error(tmp_path):
    output = process_swc_file("1", str(tmp_path / "missing.swc"))

    assert error_of(output).stage == "standard_morph"
    assert error_of(output).kind == "FileNotFoundError"
    assert output.quality_control is None


def test_output_stage_error(small_reconstruction, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(process_qc, "to_quality_control", fail)

    output = process_json("1", small_reconstruction)

    assert output.quality_control is None
    assert error_of(output).stage == "output"
    assert error_of(output).kind == "RuntimeError"
    assert error_of(output).info == "boom"


def test_nan_value_passes_through_as_null(small_reconstruction, monkeypatch):
    replaced = []

    def run_qc_with_nan(input_data, context, suite_name):
        report = standard_morph.run_qc(input_data, context, suite_name="default_pre_registration_tests")
        report.results[0] = dataclasses.replace(report.results[0], value=float("nan"))
        replaced.append(report.results[0].name)
        return report

    monkeypatch.setattr(process_qc, "run_qc", run_qc_with_nan)

    output = process_json("1", small_reconstruction)

    assert output.error is None
    assert metric(output.quality_control, replaced[0])["value"] is None


def test_neuroglancer_sources_pass_through(small_reconstruction):
    options = QualityControlOptions(skeleton_source="precomputed://s3://bucket/skeletons", segment_ids=[123],
                                    image_source="s3://bucket/image.zarr")

    output = process_json("1", small_reconstruction, options)

    for m in document_of(output)["metrics"]:
        reference = m["reference"]
        assert reference.startswith("js:neuroglancer?")
        assert "skeleton=precomputed://s3://bucket/skeletons" in reference
        assert "segments=123" in reference
        assert "image=s3://bucket/image.zarr" in reference


def test_no_reference_without_sources_or_flagged_nodes(small_reconstruction):
    output = process_json("1", small_reconstruction)

    unflagged = [m for m in document_of(output)["metrics"] if "goto" not in (m["reference"] or "")]
    assert unflagged
    assert all(m["reference"] is None for m in unflagged)


@pytest.mark.atlas
def test_real_ccf_mesh_checks(small_reconstruction):
    output = process_json("1", small_reconstruction, QualityControlOptions(is_registered=True))

    assert output.error is None
    assert metric_status(output.quality_control, "soma_inside_ccf_mesh") == "Pass"
    assert metric_status(output.quality_control, "nodes_outside_ccf_mesh") == "Pass"
