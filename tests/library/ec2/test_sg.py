import pytest
from unittest.mock import Mock, patch, call
from models.ec2.sg import Ec2SecurityGroup, Ec2SecurityGroupRule
from models.constants.constants import Environment, CostCentre, Team
from library.ec2 import sg


class TestSecurityGroupCreate:
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_with_minimal_fields(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test SG",
            strict_validation=False,
        )
        
        result = sg.create(sg_model)
        
        mock_sg_class.assert_called_once()
        assert result == mock_sg_instance
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_passes_resource_name(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        sg_model = Ec2SecurityGroup(
            name="my-security-group",
            description="Test",
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert call_kwargs['resource_name'] == "my-security-group"
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_passes_description(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="My test description",
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert call_kwargs['description'] == "My test description"
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_passes_vpc_id(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            vpc_id="vpc-12345",
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert call_kwargs['vpc_id'] == "vpc-12345"
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_passes_tags(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        tags = {
            "Environment": Environment.DEV.value,
            "Cost_centre": CostCentre.ENGINEERING.value,
            "Team": Team.SRE.value,
        }
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            tags=tags,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert "Environment" in call_kwargs['tags']
        assert call_kwargs['tags']['Environment'] == Environment.DEV.value
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_with_ingress_rules(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        ingress_rule = Ec2SecurityGroupRule(
            description="Allow HTTP",
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        )
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            ingress=[ingress_rule],
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert len(call_kwargs['ingress']) == 1
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_with_egress_rules(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        egress_rule = Ec2SecurityGroupRule(
            description="Allow all outbound",
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            egress=[egress_rule],
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert len(call_kwargs['egress']) == 1
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_with_multiple_ingress_rules(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        rules = [
            Ec2SecurityGroupRule(from_port=80, to_port=80, protocol="tcp"),
            Ec2SecurityGroupRule(from_port=443, to_port=443, protocol="tcp"),
            Ec2SecurityGroupRule(from_port=22, to_port=22, protocol="tcp"),
        ]
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            ingress=rules,
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert len(call_kwargs['ingress']) == 3
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_ingress_rule_fields(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        ingress_rule = Ec2SecurityGroupRule(
            description="SSH access",
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["10.0.0.0/8"],
            ipv6_cidr_blocks=["::/0"],
            self_reference=True,
        )
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            ingress=[ingress_rule],
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        ingress_args = call_kwargs['ingress'][0]
        
        assert ingress_args.description == "SSH access"
        assert ingress_args.from_port == 22
        assert ingress_args.to_port == 22
        assert ingress_args.protocol == "tcp"
        assert ingress_args.cidr_blocks == ["10.0.0.0/8"]
        assert ingress_args.ipv6_cidr_blocks == ["::/0"]
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_egress_rule_fields(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        egress_rule = Ec2SecurityGroupRule(
            description="All outbound",
            from_port=0,
            to_port=65535,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            self_reference=False,
        )
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            egress=[egress_rule],
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        egress_args = call_kwargs['egress'][0]
        
        assert egress_args.description == "All outbound"
        assert egress_args.from_port == 0
        assert egress_args.to_port == 65535
        assert egress_args.protocol == "tcp"
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_with_empty_ingress_list(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            ingress=[],
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert call_kwargs['ingress'] == []
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_with_empty_egress_list(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            egress=[],
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert call_kwargs['egress'] == []
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_security_group_returns_aws_resource(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_instance.id = "sg-12345"
        mock_sg_instance.arn = "arn:aws:ec2:us-east-1:123456789:security-group/sg-12345"
        mock_sg_class.return_value = mock_sg_instance
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            strict_validation=False,
        )
        
        result = sg.create(sg_model)
        
        assert result.id == "sg-12345"
        assert result.arn == "arn:aws:ec2:us-east-1:123456789:security-group/sg-12345"


class TestSecurityGroupCreateEdgeCases:
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_with_none_vpc_id(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            vpc_id=None,
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert call_kwargs['vpc_id'] is None
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_with_none_description(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description=None,
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert call_kwargs['description'] is None
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_with_rule_none_description(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        rule = Ec2SecurityGroupRule(
            description=None,
            from_port=80,
            to_port=80,
            protocol="tcp",
        )
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            ingress=[rule],
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert call_kwargs['ingress'][0].description is None
    
    @patch('library.ec2.sg.aws.ec2.SecurityGroup')
    def test_create_with_both_ingress_and_egress(self, mock_sg_class):
        mock_sg_instance = Mock()
        mock_sg_class.return_value = mock_sg_instance
        
        ingress_rule = Ec2SecurityGroupRule(
            from_port=80,
            to_port=80,
            protocol="tcp",
        )
        egress_rule = Ec2SecurityGroupRule(
            from_port=0,
            to_port=0,
            protocol="-1",
        )
        
        sg_model = Ec2SecurityGroup(
            name="test-sg",
            description="Test",
            ingress=[ingress_rule],
            egress=[egress_rule],
            strict_validation=False,
        )
        
        sg.create(sg_model)
        
        call_kwargs = mock_sg_class.call_args[1]
        assert len(call_kwargs['ingress']) == 1
        assert len(call_kwargs['egress']) == 1
