from pydantic import BaseModel, ConfigDict, Field, AliasGenerator
from pydantic.alias_generators import to_camel


class StandardMorphTest(BaseModel):
    model_config = ConfigDict(alias_generator=AliasGenerator(serialization_alias=to_camel))

    test_name: str
    test_description: str
    affected_nodes: list[int] = Field(default_factory=list)


class StandardMorpOutput(BaseModel):
    model_config = ConfigDict(alias_generator=AliasGenerator(serialization_alias=to_camel))

    standard_morph_version: str
    passed: list[StandardMorphTest] = Field(default_factory=list)
    warnings: list[StandardMorphTest] = Field(default_factory=list)
    errors: list[StandardMorphTest] = Field(default_factory=list)


class QualityControlOutput(BaseModel):
    model_config = ConfigDict(alias_generator=AliasGenerator(serialization_alias=to_camel))

    service_version: str = "3.0.2"
    reconstruction_id: str
    result: StandardMorpOutput | None = None
    error_kind: str | None = None
    error_description: str | None = None
    error_info: str | None = None
