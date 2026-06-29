from typing import List

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class NodeData(BaseModel):
    index: int
    structure: int
    x: float
    y: float
    z: float
    radius: float
    parentIndex: int


class QualityControlOptions(BaseModel):
    # validate_by_name lets Python callers pass snake_case keywords; without it they would be silently ignored.
    model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=to_camel), validate_by_name=True)

    is_registered: bool = False
    skeleton_source: str | None = None
    segment_ids: list[int | str] | None = None
    image_source: str | None = None


class ReconstructionInput(QualityControlOptions):
    id: str
    data: List[NodeData]
