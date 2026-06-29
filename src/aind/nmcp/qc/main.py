import logging
import os

from fastapi import FastAPI

from aind.nmcp.qc.quality_control_output import QualityControlOutput
from aind.nmcp.qc.reconstruction_input import ReconstructionInput
from aind.nmcp.qc.process_qc import process_node_data

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
        logger.error(f"Error processing reconstruction {item.id}: {e}")
        return QualityControlOutput(reconstruction_id=item.id, result=None, error_kind="ServiceError",
                                    error_description=f"Error processing reconstruction {item.id}",
                                    error_info=str(e))


def run():
    """Production entry point used by the ``nmcp-qc-serve`` console script."""
    import uvicorn

    uvicorn.run(
        "aind.nmcp.qc.main:app",
        host=os.environ.get("NMCP_QC_HOST", "0.0.0.0"),
        port=int(os.environ.get("NMCP_QC_PORT", "5000")),
    )


if __name__ == "__main__":
    run()
