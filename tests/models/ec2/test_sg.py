import pytest
from pydantic import ValidationError
from models.ec2.sg import (
    Ec2SecurityGroupRule,
    Ec2SecurityGroup,
    Ec2SecurityGroupConfig,
)
from models.constants.constants import AWSRegion, Environment, CostCentre, Team


class TestEc2SecurityGroupRule:
    def test_create_rule_with_required_fields(self):
        rule = Ec2SecurityGroupRule(
            from_port=80,
            to_port=80,
            protocol="tcp",
        )
        assert rule.from_port == 80
        assert rule.to_port == 80
        assert rule.protocol == "tcp"
    
    def test_create_rule_with_all_fields(self):
        rule = Ec2SecurityGroupRule(
            description="Allow HTTP",
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            ipv6_cidr_blocks=["::/0"],
            security_groups=["sg-12345"],
            self_reference=True,
        )
        assert rule.description == "Allow HTTP"
        assert rule.from_port == 80
        assert rule.to_port == 80
        assert rule.protocol == "tcp"
        assert rule.cidr_blocks == ["0.0.0.0/0"]
        assert rule.ipv6_cidr_blocks == ["::/0"]
        assert rule.security_groups == ["sg-12345"]
        assert rule.self_reference is True
    
    def test_rule_defaults_for_optional_fields(self):
        rule = Ec2SecurityGroupRule(
            from_port=443,
            to_port=443,
            protocol="tcp",
        )
        assert rule.description is None
        assert rule.cidr_blocks == []
        assert rule.ipv6_cidr_blocks == []
        assert rule.security_groups == []
        assert rule.self_reference is False
    
    def test_rule_with_port_range(self):
        rule = Ec2SecurityGroupRule(
            from_port=8000,
            to_port=9000,
            protocol="tcp",
        )
        assert rule.from_port == 8000
        assert rule.to_port == 9000
    
    def test_rule_with_multiple_cidr_blocks(self):
        cidr_blocks = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
        rule = Ec2SecurityGroupRule(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=cidr_blocks,
        )
        assert rule.cidr_blocks == cidr_blocks
    
    def test_rule_with_multiple_security_groups(self):
        security_groups = ["sg-123", "sg-456", "sg-789"]
        rule = Ec2SecurityGroupRule(
            from_port=3306,
            to_port=3306,
            protocol="tcp",
            security_groups=security_groups,
        )
        assert rule.security_groups == security_groups
    
    def test_rule_with_icmp_protocol(self):
        rule = Ec2SecurityGroupRule(
            from_port=-1,
            to_port=-1,
            protocol="icmp",
        )
        assert rule.protocol == "icmp"
    
    def test_rule_with_all_traffic(self):
        rule = Ec2SecurityGroupRule(
            from_port=-1,
            to_port=-1,
            protocol="-1",
        )
        assert rule.protocol == "-1"
    
    def test_rule_missing_required_from_port_raises_error(self):
        with pytest.raises(ValidationError):
            Ec2SecurityGroupRule(
                to_port=80,
                protocol="tcp",
            )
    
    def test_rule_missing_required_to_port_raises_error(self):
        with pytest.raises(ValidationError):
            Ec2SecurityGroupRule(
                from_port=80,
                protocol="tcp",
            )
    
    def test_rule_missing_required_protocol_raises_error(self):
        with pytest.raises(ValidationError):
            Ec2SecurityGroupRule(
                from_port=80,
                to_port=80,
            )


class TestEc2SecurityGroup:
    def test_create_security_group_with_minimal_fields(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test security group",
            strict_validation=False,
        )
        assert sg.name == "test-sg"
        assert sg.description == "Test security group"
    
    def test_create_security_group_with_all_fields(self):
        ingress_rule = Ec2SecurityGroupRule(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        )
        egress_rule = Ec2SecurityGroupRule(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
        
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test security group",
            region=AWSRegion.US_WEST_2,
            vpc_id="vpc-12345",
            ingress=[ingress_rule],
            egress=[egress_rule],
            tags={
                "Environment": Environment.DEV.value,
                "Cost_centre": CostCentre.ENGINEERING.value,
                "Team": Team.SRE.value,
            },
        )
        assert sg.name == "test-sg"
        assert sg.description == "Test security group"
        assert sg.region == AWSRegion.US_WEST_2
        assert sg.vpc_id == "vpc-12345"
        assert len(sg.ingress) == 1
        assert len(sg.egress) == 1
    
    def test_security_group_default_region(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            strict_validation=False,
        )
        assert sg.region == AWSRegion.US_EAST_1
    
    def test_security_group_default_vpc_id(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            strict_validation=False,
        )
        assert sg.vpc_id is None
    
    def test_security_group_default_ingress_rules(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            strict_validation=False,
        )
        assert sg.ingress == []
    
    def test_security_group_default_egress_rules(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            strict_validation=False,
        )
        assert sg.egress == []
    
    def test_security_group_with_multiple_ingress_rules(self):
        rules = [
            Ec2SecurityGroupRule(from_port=80, to_port=80, protocol="tcp"),
            Ec2SecurityGroupRule(from_port=443, to_port=443, protocol="tcp"),
            Ec2SecurityGroupRule(from_port=22, to_port=22, protocol="tcp"),
        ]
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            ingress=rules,
            strict_validation=False,
        )
        assert len(sg.ingress) == 3
    
    def test_security_group_with_multiple_egress_rules(self):
        rules = [
            Ec2SecurityGroupRule(from_port=80, to_port=80, protocol="tcp"),
            Ec2SecurityGroupRule(from_port=443, to_port=443, protocol="tcp"),
        ]
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            egress=rules,
            strict_validation=False,
        )
        assert len(sg.egress) == 2
    
    def test_security_group_inherits_base_resource_name_validation(self):
        sg = Ec2SecurityGroup(
            name="TEST_SG",
            description="Test",
            strict_validation=False,
        )
        assert sg.name == "test-sg"
    
    def test_security_group_inherits_base_resource_tag_behavior(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            strict_validation=False,
        )
        assert sg.tags["Name"] == "test-sg"
        assert sg.tags["Created_by"] == "pulumi"
    
    def test_security_group_with_strict_validation_requires_tags(self):
        with pytest.raises(ValidationError):
            Ec2SecurityGroup(
                name="test-sg",
                description="Test",
            )
    
    def test_security_group_with_valid_tags_and_strict_validation(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            tags={
                "Environment": Environment.PROD.value,
                "Cost_centre": CostCentre.INFRA.value,
                "Team": Team.SRE.value,
            },
        )
        assert sg.name == "test-sg"
    
    def test_security_group_description_can_be_none(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description=None,
            strict_validation=False,
        )
        assert sg.description is None


@pytest.mark.parametrize(
    "region",
    [
        AWSRegion.US_EAST_1,
        AWSRegion.US_WEST_2,
        AWSRegion.EU_CENTRAL_1,
        AWSRegion.AP_SOUTH_1,
    ],
)
def test_security_group_with_various_regions(region):
    sg = Ec2SecurityGroup(
        name="test-sg",
        description="Test",
        region=region,
        strict_validation=False,
    )
    assert sg.region == region


class TestEc2SecurityGroupConfig:
    def test_create_config_with_defaults(self):
        config = Ec2SecurityGroupConfig()
        assert config.security_groups == []
        assert config.security_group_id is None
    
    def test_create_config_with_security_groups(self):
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
        
        config = Ec2SecurityGroupConfig(security_groups=[sg1, sg2])
        assert len(config.security_groups) == 2
        assert config.security_groups[0].name == "sg1"
        assert config.security_groups[1].name == "sg2"
    
    def test_create_config_with_security_group_ids(self):
        ids = ["sg-123", "sg-456", "sg-789"]
        config = Ec2SecurityGroupConfig(security_group_id=ids)
        assert config.security_group_id == ids
    
    def test_create_config_with_both_groups_and_ids(self):
        sg = Ec2SecurityGroup(
            name="sg1",
            description="SG 1",
            strict_validation=False,
        )
        ids = ["sg-123", "sg-456"]
        
        config = Ec2SecurityGroupConfig(
            security_groups=[sg],
            security_group_id=ids,
        )
        assert len(config.security_groups) == 1
        assert len(config.security_group_id) == 2
    
    def test_config_empty_security_groups_list(self):
        config = Ec2SecurityGroupConfig(security_groups=[])
        assert config.security_groups == []
    
    def test_config_empty_security_group_ids(self):
        config = Ec2SecurityGroupConfig(security_group_id=[])
        assert config.security_group_id == []


class TestEc2SecurityGroupEdgeCases:
    def test_rule_with_zero_ports(self):
        rule = Ec2SecurityGroupRule(
            from_port=0,
            to_port=0,
            protocol="tcp",
        )
        assert rule.from_port == 0
        assert rule.to_port == 0
    
    def test_rule_with_high_port_numbers(self):
        rule = Ec2SecurityGroupRule(
            from_port=65535,
            to_port=65535,
            protocol="tcp",
        )
        assert rule.from_port == 65535
        assert rule.to_port == 65535
    
    def test_rule_with_empty_lists(self):
        rule = Ec2SecurityGroupRule(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=[],
            ipv6_cidr_blocks=[],
            security_groups=[],
        )
        assert rule.cidr_blocks == []
        assert rule.ipv6_cidr_blocks == []
        assert rule.security_groups == []
    
    def test_security_group_with_empty_description(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="",
            strict_validation=False,
        )
        assert sg.description == ""
    
    def test_security_group_with_long_description(self):
        long_desc = "A" * 1000
        sg = Ec2SecurityGroup(
            name="test-sg",
            description=long_desc,
            strict_validation=False,
        )
        assert sg.description == long_desc
    
    def test_rule_with_udp_protocol(self):
        rule = Ec2SecurityGroupRule(
            from_port=53,
            to_port=53,
            protocol="udp",
        )
        assert rule.protocol == "udp"
    
    def test_rule_self_reference_true(self):
        rule = Ec2SecurityGroupRule(
            from_port=3306,
            to_port=3306,
            protocol="tcp",
            self_reference=True,
        )
        assert rule.self_reference is True
    
    def test_rule_self_reference_false(self):
        rule = Ec2SecurityGroupRule(
            from_port=3306,
            to_port=3306,
            protocol="tcp",
            self_reference=False,
        )
        assert rule.self_reference is False
    
    def test_security_group_get_pulumi_dict(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            strict_validation=False,
        )
        pulumi_dict = sg.get_pulumi_dict()
        
        assert isinstance(pulumi_dict, dict)
        assert "name" in pulumi_dict
        assert "description" in pulumi_dict
        assert "region" in pulumi_dict
    
    def test_security_group_resource_name_property(self):
        sg = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            strict_validation=False,
        )
        assert sg.resource_name == "test-sg"
