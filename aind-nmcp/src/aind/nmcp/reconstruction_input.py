from typing import List

from pydantic import BaseModel

class NodeData(BaseModel):
    index: int
    structure: int
    x: float
    y: float
    z: float
    radius: float
    parentIndex: int

class ReconstructionInput(BaseModel):
    id: str
    data: List[NodeData]
