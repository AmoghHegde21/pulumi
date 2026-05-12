import pulumi_aws as aws
from models.ec2.instance import Ec2InstanceResource
from library.ec2.sg import create as sg_create

instance_outputs = {}


def create(instance: Ec2InstanceResource):
    sg_ids = []

    if (
            instance.security_group
            and instance.security_group.security_group_id
    ):
        sg_ids.extend(instance.security_group.security_group_id)
    elif (
            instance.security_group
            and instance.security_group.security_groups
    ):
        for sg in instance.security_group.security_groups:
            ec2_sg = sg_create(sg)
            sg_ids.append(ec2_sg.id)
    ec2_instance = aws.ec2.Instance(
        instance.name,
        ami=instance.ami,
        instance_type=instance.instance_type,
        key_name=instance.key_name,
        vpc_security_group_ids=sg_ids if sg_ids else None,
        tags=instance.tags
    )

    instance_outputs[instance.name] = {
        "instance_id": ec2_instance.id,
        "public_ip": ec2_instance.public_ip,
        "security_group_ids": sg_ids,
    }

    return instance_outputs
