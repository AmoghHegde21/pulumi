from provider.config_provider import ConfigProvider
from models.ec2.instance import Ec2InstanceConfig
from library.ec2.instance import create
import pulumi


def create_resource(account_id: str, region: str, module: str, sub_module: str):
    instance_list = ConfigProvider.load(
        config_path=f"configs/{account_id}/{region}/{module}/{sub_module}",
        model_class=Ec2InstanceConfig
    )

    outputs = {}
    for instance in instance_list.instances:
        outputs.update(create(instance))

    pulumi.export("instances", outputs)
