import json
import logging
from typing import Any

from aind_neuron_reconstruction_io.io import parse_json

from standard_morph.Standardizer import Standardizer

from .quality_control_output import QualityControlOutput, StandardMorpOutput

from .quality_control_output import StandardMorphError

logger = logging.getLogger(__name__)

_ERRORS_AS_WARNINGS = ("AxonOrigins", "DendriteOrigins")


def process(reconstruction_id: str, json_contents: Any) -> QualityControlOutput:
    data = parse_json(json_contents, False)

    worker = Standardizer(path_to_swc=None, input_morphology_df=data, swc_separator=" ")

    """
    worker = Standardizer(
        path_to_swc=None,
        swc_separator="\s+",
        soma_children_distance_threshold=50,
        valid_filename_format="None",
        soma_mip_kwargs={}
    )
    """

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


if __name__ == '__main__':
    with open("../../../tests/test_data/small_reconstruction.json", "r") as f:
        contents = f.read()

    output = process("609281", json.loads(contents))

    print(output)
