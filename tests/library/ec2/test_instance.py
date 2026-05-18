import pytest
from unittest.mock import Mock, patch, MagicMock
from models.ec2.instance import Ec2InstanceResource
from models.ec2.sg import Ec2SecurityGroup, Ec2SecurityGroupConfig
from library.ec2 import instance


class TestInstanceCreate:
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_with_minimal_fields(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        instance_model = Ec2InstanceResource(
            name="test-instance",
            ami="ami-12345",
            instance_type="t2.micro",
            key_name="my-key",
            strict_validation=False,
        )
        
        result = instance.create(instance_model)
        
        mock_instance_class.assert_called_once()
        assert "test-instance" in result
        assert result["test-instance"]["instance_id"] == "i-12345"
    
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_passes_ami(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-abcdef",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        call_kwargs = mock_instance_class.call_args[1]
        assert call_kwargs['ami'] == "ami-abcdef"
    
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_passes_instance_type(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t3.large",
            key_name="key",
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        call_kwargs = mock_instance_class.call_args[1]
        assert call_kwargs['instance_type'] == "t3.large"
    
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_passes_key_name(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="my-special-key",
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        call_kwargs = mock_instance_class.call_args[1]
        assert call_kwargs['key_name'] == "my-special-key"
    
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_passes_tags(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        call_kwargs = mock_instance_class.call_args[1]
        assert "Name" in call_kwargs['tags']
        assert call_kwargs['tags']['Created_by'] == "pulumi"
    
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_without_security_group(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            security_group=None,
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        call_kwargs = mock_instance_class.call_args[1]
        assert call_kwargs['vpc_security_group_ids'] is None
    
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_with_security_group_ids(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        sg_config = Ec2SecurityGroupConfig(
            security_group_id=["sg-111", "sg-222"]
        )
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            security_group=sg_config,
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        call_kwargs = mock_instance_class.call_args[1]
        assert call_kwargs['vpc_security_group_ids'] == ["sg-111", "sg-222"]
    
    @patch('library.ec2.instance.sg_create')
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_with_security_groups_creates_them(self, mock_instance_class, mock_sg_create):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        mock_sg1 = Mock()
        mock_sg1.id = "sg-created-1"
        mock_sg2 = Mock()
        mock_sg2.id = "sg-created-2"
        mock_sg_create.side_effect = [mock_sg1, mock_sg2]
        
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
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            security_group=sg_config,
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        assert mock_sg_create.call_count == 2
        call_kwargs = mock_instance_class.call_args[1]
        assert "sg-created-1" in call_kwargs['vpc_security_group_ids']
        assert "sg-created-2" in call_kwargs['vpc_security_group_ids']
    
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_returns_outputs_dict(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "54.1.2.3"
        mock_instance_class.return_value = mock_instance_obj
        
        instance_model = Ec2InstanceResource(
            name="my-instance",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        
        result = instance.create(instance_model)
        
        assert "my-instance" in result
        assert result["my-instance"]["instance_id"] == "i-12345"
        assert result["my-instance"]["public_ip"] == "54.1.2.3"
        assert "security_group_ids" in result["my-instance"]
    
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_stores_in_instance_outputs(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-99999"
        mock_instance_obj.public_ip = "10.0.0.1"
        mock_instance_class.return_value = mock_instance_obj
        
        instance.instance_outputs.clear()
        
        instance_model = Ec2InstanceResource(
            name="stored-instance",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        assert "stored-instance" in instance.instance_outputs
        assert instance.instance_outputs["stored-instance"]["instance_id"] == "i-99999"


class TestInstanceCreateEdgeCases:
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_with_empty_security_group_ids_list(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        sg_config = Ec2SecurityGroupConfig(
            security_group_id=[]
        )
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            security_group=sg_config,
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        call_kwargs = mock_instance_class.call_args[1]
        assert call_kwargs['vpc_security_group_ids'] is None
    
    @patch('library.ec2.instance.sg_create')
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_with_empty_security_groups_list(self, mock_instance_class, mock_sg_create):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        sg_config = Ec2SecurityGroupConfig(
            security_groups=[]
        )
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            security_group=sg_config,
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        mock_sg_create.assert_not_called()
        call_kwargs = mock_instance_class.call_args[1]
        assert call_kwargs['vpc_security_group_ids'] is None
    
    @patch('library.ec2.instance.sg_create')
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_prioritizes_security_group_ids_over_groups(self, mock_instance_class, mock_sg_create):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = "1.2.3.4"
        mock_instance_class.return_value = mock_instance_obj
        
        sg = Ec2SecurityGroup(
            name="sg1",
            description="SG 1",
            strict_validation=False,
        )
        
        sg_config = Ec2SecurityGroupConfig(
            security_group_id=["sg-existing"],
            security_groups=[sg]
        )
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            security_group=sg_config,
            strict_validation=False,
        )
        
        instance.create(instance_model)
        
        mock_sg_create.assert_not_called()
        call_kwargs = mock_instance_class.call_args[1]
        assert call_kwargs['vpc_security_group_ids'] == ["sg-existing"]
    
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_multiple_instances_updates_outputs(self, mock_instance_class):
        instance.instance_outputs.clear()
        
        mock_instance1 = Mock()
        mock_instance1.id = "i-111"
        mock_instance1.public_ip = "1.1.1.1"
        
        mock_instance2 = Mock()
        mock_instance2.id = "i-222"
        mock_instance2.public_ip = "2.2.2.2"
        
        mock_instance_class.side_effect = [mock_instance1, mock_instance2]
        
        instance1_model = Ec2InstanceResource(
            name="instance1",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        
        instance2_model = Ec2InstanceResource(
            name="instance2",
            ami="ami-456",
            instance_type="t2.small",
            key_name="key",
            strict_validation=False,
        )
        
        instance.create(instance1_model)
        instance.create(instance2_model)
        
        assert len(instance.instance_outputs) == 2
        assert "instance1" in instance.instance_outputs
        assert "instance2" in instance.instance_outputs
    
    @patch('library.ec2.instance.aws.ec2.Instance')
    def test_create_instance_with_none_public_ip(self, mock_instance_class):
        mock_instance_obj = Mock()
        mock_instance_obj.id = "i-12345"
        mock_instance_obj.public_ip = None
        mock_instance_class.return_value = mock_instance_obj
        
        instance_model = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        
        result = instance.create(instance_model)
        
        assert result["test"]["public_ip"] is None
