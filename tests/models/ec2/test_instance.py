import pytest
from pydantic import ValidationError
from models.ec2.instance import Ec2InstanceResource, Ec2InstanceConfig
from models.ec2.sg import Ec2SecurityGroupConfig, Ec2SecurityGroup
from models.constants.constants import Environment, CostCentre, Team, AWSRegion


class TestEc2InstanceResource:
    def test_create_instance_with_required_fields(self):
        instance = Ec2InstanceResource(
            name="test-instance",
            ami="ami-12345678",
            instance_type="t2.micro",
            key_name="my-key",
            strict_validation=False,
        )
        assert instance.name == "test-instance"
        assert instance.ami == "ami-12345678"
        assert instance.instance_type == "t2.micro"
        assert instance.key_name == "my-key"
    
    def test_create_instance_with_all_fields(self):
        sg_config = Ec2SecurityGroupConfig(
            security_group_id=["sg-123", "sg-456"]
        )
        instance = Ec2InstanceResource(
            name="test-instance",
            ami="ami-12345678",
            instance_type="t3.large",
            key_name="my-key",
            security_group=sg_config,
            tags={
                "Environment": Environment.PROD.value,
                "Cost_centre": CostCentre.ENGINEERING.value,
                "Team": Team.SRE.value,
            },
        )
        assert instance.name == "test-instance"
        assert instance.ami == "ami-12345678"
        assert instance.instance_type == "t3.large"
        assert instance.key_name == "my-key"
        assert instance.security_group is not None
        assert len(instance.security_group.security_group_id) == 2
    
    def test_instance_default_security_group_is_none(self):
        instance = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        assert instance.security_group is None
    
    def test_instance_inherits_base_resource_name_validation(self):
        instance = Ec2InstanceResource(
            name="TEST_Instance",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        assert instance.name == "test-instance"
    
    def test_instance_inherits_base_resource_tag_behavior(self):
        instance = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        assert instance.tags["Name"] == "test"
        assert instance.tags["Created_by"] == "pulumi"
    
    def test_instance_with_strict_validation_requires_tags(self):
        with pytest.raises(ValidationError):
            Ec2InstanceResource(
                name="test",
                ami="ami-123",
                instance_type="t2.micro",
                key_name="key",
            )
    
    def test_instance_missing_ami_raises_error(self):
        with pytest.raises(ValidationError):
            Ec2InstanceResource(
                name="test",
                instance_type="t2.micro",
                key_name="key",
                strict_validation=False,
            )
    
    def test_instance_missing_instance_type_raises_error(self):
        with pytest.raises(ValidationError):
            Ec2InstanceResource(
                name="test",
                ami="ami-123",
                key_name="key",
                strict_validation=False,
            )
    
    def test_instance_missing_key_name_raises_error(self):
        with pytest.raises(ValidationError):
            Ec2InstanceResource(
                name="test",
                ami="ami-123",
                instance_type="t2.micro",
                strict_validation=False,
            )
    
    @pytest.mark.parametrize(
        ("instance_type"),
        [
            "t2.micro",
            "t2.small",
            "t2.medium",
            "t3.micro",
            "t3.small",
            "t3.medium",
            "t3.large",
            "m5.large",
            "m5.xlarge",
            "c5.large",
        ],
    )
    def test_instance_with_various_instance_types(self, instance_type):
        instance = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type=instance_type,
            key_name="key",
            strict_validation=False,
        )
        assert instance.instance_type == instance_type
    
    def test_instance_with_security_group_config_with_ids(self):
        sg_config = Ec2SecurityGroupConfig(
            security_group_id=["sg-111", "sg-222", "sg-333"]
        )
        instance = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            security_group=sg_config,
            strict_validation=False,
        )
        assert len(instance.security_group.security_group_id) == 3
    
    def test_instance_with_security_group_config_with_groups(self):
        sg1 = Ec2SecurityGroup(
            name="sg1",
            description="SG 1",
            strict_validation=False,
        )
        sg2 = Ec2SecurityGroup(
            name="sg2",
            description="SG 2",
            strict_validation=False,
        )
        sg_config = Ec2SecurityGroupConfig(
            security_groups=[sg1, sg2]
        )
        instance = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            security_group=sg_config,
            strict_validation=False,
        )
        assert len(instance.security_group.security_groups) == 2
    
    def test_instance_get_pulumi_dict(self):
        instance = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        pulumi_dict = instance.get_pulumi_dict()
        
        assert isinstance(pulumi_dict, dict)
        assert "name" in pulumi_dict
        assert "ami" in pulumi_dict
        assert "instance_type" in pulumi_dict
        assert "key_name" in pulumi_dict
    
    def test_instance_resource_name_property(self):
        instance = Ec2InstanceResource(
            name="test-instance",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        assert instance.resource_name == "test-instance"


class TestEc2InstanceConfig:
    def test_create_config_with_defaults(self):
        config = Ec2InstanceConfig()
        assert config.instances == []
    
    def test_create_config_with_instances(self):
        instance1 = Ec2InstanceResource(
            name="instance1",
            ami="ami-111",
            instance_type="t2.micro",
            key_name="key1",
            strict_validation=False,
        )
        instance2 = Ec2InstanceResource(
            name="instance2",
            ami="ami-222",
            instance_type="t2.small",
            key_name="key2",
            strict_validation=False,
        )
        
        config = Ec2InstanceConfig(instances=[instance1, instance2])
        assert len(config.instances) == 2
        assert config.instances[0].name == "instance1"
        assert config.instances[1].name == "instance2"
    
    def test_create_config_with_empty_list(self):
        config = Ec2InstanceConfig(instances=[])
        assert config.instances == []
    
    def test_config_with_multiple_instances_different_types(self):
        instances = [
            Ec2InstanceResource(
                name=f"instance-{i}",
                ami=f"ami-{i}",
                instance_type=instance_type,
                key_name=f"key-{i}",
                strict_validation=False,
            )
            for i, instance_type in enumerate(["t2.micro", "t3.small", "m5.large"])
        ]
        
        config = Ec2InstanceConfig(instances=instances)
        assert len(config.instances) == 3
        assert config.instances[0].instance_type == "t2.micro"
        assert config.instances[1].instance_type == "t3.small"
        assert config.instances[2].instance_type == "m5.large"


class TestEc2InstanceEdgeCases:
    def test_instance_with_long_ami_string(self):
        long_ami = "ami-" + "a" * 100
        instance = Ec2InstanceResource(
            name="test",
            ami=long_ami,
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        assert instance.ami == long_ami
    
    def test_instance_with_special_characters_in_key_name(self):
        instance = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="my-key_name.pem",
            strict_validation=False,
        )
        assert instance.key_name == "my-key_name.pem"
    
    def test_instance_with_none_security_group_explicitly(self):
        instance = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            security_group=None,
            strict_validation=False,
        )
        assert instance.security_group is None
