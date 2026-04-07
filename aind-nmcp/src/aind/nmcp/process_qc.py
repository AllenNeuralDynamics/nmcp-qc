import logging
from typing import Any, List

import pandas as pd

from aind_neuron_reconstruction_io.io import parse_json

from standard_morph.Standardizer import Standardizer

from .quality_control_output import QualityControlOutput, StandardMorpOutput

from .quality_control_output import StandardMorphTest
from .reconstruction_input import NodeData

logger = logging.getLogger(__name__)

_TESTS_AS_ERROR = ("DendriteOrigins", "CheckForLoops", "OrphanedNodes", "AxonOrigins", "NumberOfSomas")


def process_swc_file(reconstruction_id: str, file: str) -> QualityControlOutput:
    worker = Standardizer(
        path_to_swc=file,
        swc_separator=" ",
        soma_children_distance_threshold=50,
        soma_mip_kwargs={},
        write_all_tests_to_report=True
    )

    return _process(reconstruction_id, worker)

def process_node_data(reconstruction_id: str, node_data: List[NodeData]) -> QualityControlOutput:
    try:
        col_list = [
            "node_id",
            "compartment",
            "x",
            "y",
            "z",
            "r",
            "parent",
        ]

        node_list = [list(n.model_dump().values()) for n in node_data]

        data = pd.DataFrame(node_list, columns=col_list)

        worker = Standardizer(
            path_to_swc=None,
            input_morphology_df=data,
            swc_separator=" ",
            soma_children_distance_threshold=50,
            soma_mip_kwargs={},
            write_all_tests_to_report=True
        )

        return _process(reconstruction_id, worker)

    except Exception as error:
        return QualityControlOutput(reconstruction_id=reconstruction_id, result=None, error_kind="ParseError",
                                    error_description="An unexpected error occurred parsing the reconstruction data.",
                                    error_info=str(error))

def process_json(reconstruction_id: str, json_contents: Any) -> QualityControlOutput:
    try:
        data = parse_json(json_contents, False)
    except KeyError as key_error:
        return QualityControlOutput(reconstruction_id=reconstruction_id, result=None, error_kind="KeyError",
                                    error_description="The reconstruction may reference parent nodes that are not present in the file.",
                                    error_info=str(key_error))
    except Exception as error:
        return QualityControlOutput(reconstruction_id=reconstruction_id, result=None, error_kind="ParseError",
                                    error_description="An unexpected error occurred parsing the reconstruction data.",
                                    error_info=str(error))

    worker = Standardizer(path_to_swc=None, input_morphology_df=data, swc_separator=" ",
                          soma_children_distance_threshold=50, write_all_tests_to_report=True)

    return _process(reconstruction_id, worker)


def _process(reconstruction_id: str, worker: Standardizer) -> QualityControlOutput:
    worker.validate()

    report = worker.StandardizationReport

    sm_result = StandardMorpOutput(standard_morph_version=report["StandardMorphVersion"])

    error_test_names = {error["test"] for error in report["errors"]}

    for test in report["tests"]:
        if test["test"] not in error_test_names:
            sm_result.passed.append(StandardMorphTest(test_name=test["test"], test_description=test["description"]))

    for error in report["errors"]:
        if error["test"] in _TESTS_AS_ERROR:
            sm_result.errors.append(StandardMorphTest(
                test_name=error["test"],
                test_description=error["description"],
                affected_nodes=[n[0] for n in error["nodes_with_error"]])
            )
        else:
            sm_result.warnings.append(StandardMorphTest(
                test_name=error["test"],
                test_description=error["description"],
                affected_nodes=[n[0] for n in error["nodes_with_error"]])
            )

    qc_output = QualityControlOutput(reconstruction_id=reconstruction_id, result=sm_result)

    logger.info(f"Processed reconstruction {reconstruction_id} with {len(sm_result.errors)} errors found.")

    return qc_output
