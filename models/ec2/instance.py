from pydantic import BaseModel, Field
from models.base.base_resource import BaseResource
from models.ec2.sg import Ec2SecurityGroupConfig


class Ec2InstanceResource(BaseResource):
    ami: str
    instance_type: str
    key_name: str
    security_group: Ec2SecurityGroupConfig | None = None


class Ec2InstanceConfig(BaseModel):
    instances: list[Ec2InstanceResource] = Field(default_factory=list)
