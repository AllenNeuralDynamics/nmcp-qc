from typing import Any

from pydantic import BaseModel


class ReconstructionInput(BaseModel):
    id: str
    data: Any
