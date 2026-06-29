import json
import logging
import os
from collections.abc import Callable
from typing import Any, List

import pandas as pd
from aind_neuron_reconstruction_io.io import parse_json
from standard_morph import QCContext, RunReport, Space, run_qc
from standard_morph.data_schema import to_quality_control

from .quality_control_output import QualityControlOutput, ServiceError, ServiceErrorStage
from .reconstruction_input import NodeData, QualityControlOptions

logger = logging.getLogger(__name__)

_SWC_COLUMNS = ["node_id", "compartment", "x", "y", "z", "r", "parent"]

_SUITE_WITH_CCF_MESH = "default_post_registration_tests"
_SUITE_WITHOUT_CCF_MESH = "default_pre_registration_tests"


def process_swc_file(
    reconstruction_id: str, file: str | os.PathLike[str], options: QualityControlOptions | None = None
) -> QualityControlOutput:
    # run_qc accepts a path only as str; a pathlib.Path would raise TypeError inside it.
    return _run(reconstruction_id, lambda: os.fspath(file), options)


def process_node_data(
    reconstruction_id: str, node_data: List[NodeData], options: QualityControlOptions | None = None
) -> QualityControlOutput:
    def load_input() -> pd.DataFrame:
        return pd.DataFrame([list(n.model_dump().values()) for n in node_data], columns=_SWC_COLUMNS)

    return _run(reconstruction_id, load_input, options)


def process_json(
    reconstruction_id: str, json_contents: Any, options: QualityControlOptions | None = None
) -> QualityControlOutput:
    return _run(reconstruction_id, lambda: parse_json(json_contents, False), options)


def process_json_file(
    reconstruction_id: str, path: str | os.PathLike[str], options: QualityControlOptions | None = None
) -> QualityControlOutput:
    def load_input() -> pd.DataFrame:
        with open(path, "r") as f:
            contents = json.load(f)
        return parse_json(contents, False)

    return _run(reconstruction_id, load_input, options)


def _run(
    reconstruction_id: str, load_input: Callable[[], Any], options: QualityControlOptions | None
) -> QualityControlOutput:
    options = options or QualityControlOptions()
    output = QualityControlOutput(reconstruction_id=reconstruction_id)

    try:
        input_data = load_input()
    except Exception as error:
        if isinstance(error, KeyError):
            description = "The reconstruction may reference parent nodes that are not present in the file."
        else:
            description = "An unexpected error occurred parsing the reconstruction data."
        output.error = ServiceError(stage=ServiceErrorStage.INPUT, kind=type(error).__name__,
                                    description=description, info=str(error))
        logger.warning(f"Could not load reconstruction {reconstruction_id}: {error!r}")
        return output

    if options.is_registered:
        space, suite_name = Space.CCF_REGISTERED, _SUITE_WITH_CCF_MESH
    else:
        space, suite_name = Space.IMAGE_SPACE, _SUITE_WITHOUT_CCF_MESH

    try:
        context = QCContext(space=space)
        report = run_qc(input_data, context, suite_name=suite_name)
    except Exception as error:
        output.error = ServiceError(stage=ServiceErrorStage.STANDARD_MORPH, kind=type(error).__name__,
                                    description="standard-morph raised an exception while running quality control.",
                                    info=str(error))
        logger.exception(f"standard-morph failed for reconstruction {reconstruction_id}.")
        return output

    try:
        output.quality_control = _quality_control_document(report, options)
    except Exception as error:
        output.error = ServiceError(stage=ServiceErrorStage.OUTPUT, kind=type(error).__name__,
                                    description="The QC-portal document could not be built from the standard-morph report.",
                                    info=str(error))
        logger.exception(f"Could not build the QC-portal document for reconstruction {reconstruction_id}.")
        return output

    logger.info(f"Processed reconstruction {reconstruction_id}: {report.summary.get('overall_status')}.")

    return output


def _quality_control_document(report: RunReport, options: QualityControlOptions) -> dict[str, Any]:
    document = to_quality_control(report, skeleton=options.skeleton_source, segments=options.segment_ids,
                                  image=options.image_source).model_dump(mode="json")

    # FastAPI serializes the response after the handler returns, where a failure would surface as a bare 500,
    # so prove the document is strict JSON here, inside the output stage.
    json.dumps(document, allow_nan=False)

    return document
