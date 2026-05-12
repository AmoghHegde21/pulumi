from pydantic import BaseModel
from models.base.base_resource import BaseResource
from models.constants.constants import *
from pydantic import Field


class Ec2SecurityGroupRule(BaseModel):
    description: str | None = None
    from_port: int
    to_port: int
    protocol: str
    cidr_blocks: list[str] | None = []
    ipv6_cidr_blocks: list[str] | None = []
    security_groups: list[str] | None = []
    self_reference: bool | None = False


class Ec2SecurityGroup(BaseResource):
    description: str | None
    region: AWSRegion | None = AWSRegion.US_EAST_1
    vpc_id: str | None = None
    ingress: list[Ec2SecurityGroupRule] = []
    egress: list[Ec2SecurityGroupRule] = []


class Ec2SecurityGroupConfig(BaseModel):
    security_groups: list[Ec2SecurityGroup] = Field(default_factory=list)
    security_group_id: list[str] | None = None
