from pydantic import BaseModel, ConfigDict, Field, AliasGenerator
from pydantic.alias_generators import to_camel


class StandardMorphError(BaseModel):
    model_config = ConfigDict(
       alias_generator=AliasGenerator(
           serialization_alias=to_camel)
    )
    test_name: str
    test_description: str
    affected_nodes: list[int] = Field(default_factory=list)


class StandardMorpOutput(BaseModel):
    model_config = ConfigDict(
       alias_generator=AliasGenerator(
           serialization_alias=to_camel)
    )
    standard_morph_version: str
    warnings: list[StandardMorphError] = Field(default_factory=list)
    errors: list[StandardMorphError] = Field(default_factory=list)

class QualityControlOutput(BaseModel):
    model_config = ConfigDict(
       alias_generator=AliasGenerator(
           serialization_alias=to_camel)
    )
    reconstruction_id: str
    result: StandardMorpOutput | None = None
    error_kind: str | None = None
    error_description: str | None = None
    error_info: str | None = None
