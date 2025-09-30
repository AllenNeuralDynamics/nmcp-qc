import logging
from typing import Optional, Any

from fastapi import FastAPI

from aind.nmcp.quality_control_output import QualityControlOutput
from aind.nmcp.reconstruction_input import ReconstructionInput
from aind.nmcp.process_qc import process_json

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
def read_root():
    return "NMCP Quality Control API"


@app.post("/performqc/")
async def create_item(item: ReconstructionInput) -> Optional[Any]:
    try:
        return process_json(item.id, item.data)
    except Exception as e:
        # Log the error for debugging purposes
        logger.error(f"Error processing reconstruction {item.id}: {e}")
        return QualityControlOutput(reconstruction_id=item.id, result=None, error=str(e))
