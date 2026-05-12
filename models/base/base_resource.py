import abc
from typing import Dict

from pydantic_core import PydanticCustomError
import re
from pydantic import BaseModel, Field, model_validator, field_validator

from models.constants.constants import *

TAG_VALIDATIONS = {
    "Environment": Environment,
    "Cost_centre": CostCentre,
    "Team": Team,
}


class Resource(BaseModel, abc.ABC):
    name: str = Field("")
    tags: Dict[str, str] = Field({})
    strict_validation: bool = Field(True, exclude=True, repr=False)


class BaseResource(Resource):

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        # normalize name
        value = value.strip().lower().replace("_", "-")

        # aws naming validation
        if not re.fullmatch(AWS_NAME_REGEX, value):
            raise PydanticCustomError(
                "invalid_name",
                "Name must contain only alphanumeric characters and hyphens",
            )

        if len(value) > AWS_NAME_MAX_LENGTH:
            raise PydanticCustomError(
                "invalid_name_length",
                f"Name length must be less than {AWS_NAME_MAX_LENGTH + 1} characters",
            )

        return value

    def model_post_init(self, __context) -> None:
        if 'Name' not in self.tags:
            self.tags['Name'] = self.name

        self.tags['Created_by'] = "pulumi"

    def get_pulumi_dict(self):
        return self.model_dump()

    @property
    def resource_name(self) -> str:
        return self.name

    @model_validator(mode="after")
    def tags_validations(self) -> "BaseResource":

        if not self.strict_validation:
            return self

        for tag_name, enum_class in TAG_VALIDATIONS.items():

            tag_value = self.tags.get(tag_name)

            if tag_value is None:
                raise PydanticCustomError(
                    f"missing_{tag_name.lower()}",
                    f"The tag '{tag_name}' is required",
                )

            allowed_values = [item.value for item in enum_class]

            if tag_value not in allowed_values:
                raise PydanticCustomError(
                    f"invalid_{tag_name.lower()}",
                    f"Invalid value '{tag_value}' for tag '{tag_name}'. "
                    f"Allowed values: {allowed_values}",
                )

        return self
