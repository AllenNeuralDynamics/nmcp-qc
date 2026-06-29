from enum import StrEnum
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


def _installed_version(distribution: str) -> str:
    try:
        return version(distribution)
    except PackageNotFoundError:
        return "unknown"


SERVICE_VERSION = _installed_version("nmcpqc")
STANDARD_MORPH_VERSION = _installed_version("standard-morph")


class ServiceErrorStage(StrEnum):
    INPUT = "input"
    STANDARD_MORPH = "standard_morph"
    OUTPUT = "output"


class ServiceError(BaseModel):
    model_config = ConfigDict(alias_generator=AliasGenerator(serialization_alias=to_camel))

    stage: ServiceErrorStage
    kind: str
    description: str
    info: str | None = None


class QualityControlOutput(BaseModel):
    model_config = ConfigDict(alias_generator=AliasGenerator(serialization_alias=to_camel))

    service_version: str = SERVICE_VERSION
    standard_morph_version: str = STANDARD_MORPH_VERSION
    reconstruction_id: str
    quality_control: dict[str, Any] | None = None
    error: ServiceError | None = None
