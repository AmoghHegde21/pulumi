import pulumi_aws as aws
from models.ec2.sg import Ec2SecurityGroup


def create(sg: Ec2SecurityGroup):
    security_group = aws.ec2.SecurityGroup(
        resource_name=sg.name,

        description=sg.description,

        vpc_id=sg.vpc_id,

        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                description=rule.description,
                from_port=rule.from_port,
                to_port=rule.to_port,
                protocol=rule.protocol,
                cidr_blocks=rule.cidr_blocks,
                ipv6_cidr_blocks=rule.ipv6_cidr_blocks,
                self=rule.self_reference,
            )
            for rule in sg.ingress
        ],

        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                description=rule.description,
                from_port=rule.from_port,
                to_port=rule.to_port,
                protocol=rule.protocol,
                cidr_blocks=rule.cidr_blocks,
                ipv6_cidr_blocks=rule.ipv6_cidr_blocks,
                self=rule.self_reference,
            )
            for rule in sg.egress
        ],

        tags=sg.tags
    )

    return security_group
