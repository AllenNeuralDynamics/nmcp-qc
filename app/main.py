import logging
from typing import Optional, Any

from fastapi import FastAPI

from aind.nmcp.quality_control_output import QualityControlOutput
from aind.nmcp.reconstruction_input import ReconstructionInput
from aind.nmcp.process_qc import process_node_data

uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = True

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
def read_root():
    return "NMCP Quality Control API"


@app.post("/performqc/")
async def create_item(item: ReconstructionInput) -> QualityControlOutput:
    try:
        return process_node_data(item.id, item.data)
    except Exception as e:
        # Log the error for debugging purposes
        logger.error(f"Error processing reconstruction {item.id}: {e}")
        return QualityControlOutput(reconstruction_id=item.id, result=None, error_kind="ServiceError",
                                    error_description=f"Error processing reconstruction {item.id}",
                                    error_info=str(e))
