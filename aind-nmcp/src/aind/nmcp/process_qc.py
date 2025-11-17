import logging
from typing import Any

from aind_neuron_reconstruction_io.io import parse_json

from standard_morph.Standardizer import Standardizer

from .quality_control_output import QualityControlOutput, StandardMorpOutput

from .quality_control_output import StandardMorphError

logger = logging.getLogger(__name__)

_ERRORS_AS_WARNINGS = ("SomaChildrenFurcation",)


def process_swc(reconstruction_id: str, file: str) -> QualityControlOutput:
    worker = Standardizer(
        path_to_swc=file,
        swc_separator="\s+",
        soma_children_distance_threshold=50,
        soma_mip_kwargs={}
    )
    return _process(reconstruction_id, worker)


def process_json(reconstruction_id: str, json_contents: Any) -> QualityControlOutput:
    data = parse_json(json_contents, False)

    worker = Standardizer(path_to_swc=None, input_morphology_df=data, swc_separator=" ",
                          soma_children_distance_threshold=50)

    return _process(reconstruction_id, worker)


def _process(reconstruction_id: str, worker: Standardizer) -> QualityControlOutput:
    worker.validate()

    report = worker.StandardizationReport

    sm_result = StandardMorpOutput(standard_morph_version=report["StandardMorphVersion"])

    for error in report["errors"]:
        if error["test"] in _ERRORS_AS_WARNINGS:
            sm_result.warnings.append(StandardMorphError(
                test_name=error["test"],
                test_description=error["description"],
                affected_nodes=[n[0] for n in error["nodes_with_error"]])
            )
        else:
            sm_result.errors.append(StandardMorphError(
                test_name=error["test"],
                test_description=error["description"],
                affected_nodes=[n[0] for n in error["nodes_with_error"]])
            )

    qc_output = QualityControlOutput(reconstruction_id=reconstruction_id, result=sm_result, error=None)

    logger.info(f"Processed reconstruction {reconstruction_id} with {len(sm_result.errors)} errors found.")

    return qc_output
