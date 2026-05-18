import pytest
from unittest.mock import Mock, patch, MagicMock
from models.ec2.instance import Ec2InstanceConfig, Ec2InstanceResource
from modules import ec2_instance


class TestCreateResource:
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_loads_config(self, mock_load, mock_create, mock_export):
        mock_config = Ec2InstanceConfig(instances=[])
        mock_load.return_value = mock_config
        mock_create.return_value = {}
        
        ec2_instance.create_resource(
            account_id="123456789",
            region="us-east-1",
            module="ec2",
            sub_module="instances"
        )
        
        mock_load.assert_called_once_with(
            config_path="configs/123456789/us-east-1/ec2/instances",
            model_class=Ec2InstanceConfig
        )
    
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_creates_instances(self, mock_load, mock_create, mock_export):
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
        
        mock_config = Ec2InstanceConfig(instances=[instance1, instance2])
        mock_load.return_value = mock_config
        
        mock_create.side_effect = [
            {"instance1": {"instance_id": "i-111"}},
            {"instance2": {"instance_id": "i-222"}}
        ]
        
        ec2_instance.create_resource(
            account_id="123456789",
            region="us-east-1",
            module="ec2",
            sub_module="instances"
        )
        
        assert mock_create.call_count == 2
        mock_create.assert_any_call(instance1)
        mock_create.assert_any_call(instance2)
    
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_exports_outputs(self, mock_load, mock_create, mock_export):
        instance = Ec2InstanceResource(
            name="test-instance",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        
        mock_config = Ec2InstanceConfig(instances=[instance])
        mock_load.return_value = mock_config
        
        mock_create.return_value = {
            "test-instance": {
                "instance_id": "i-12345",
                "public_ip": "1.2.3.4"
            }
        }
        
        ec2_instance.create_resource(
            account_id="123456789",
            region="us-east-1",
            module="ec2",
            sub_module="instances"
        )
        
        mock_export.assert_called_once_with("instances", {
            "test-instance": {
                "instance_id": "i-12345",
                "public_ip": "1.2.3.4"
            }
        })
    
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_with_no_instances(self, mock_load, mock_create, mock_export):
        mock_config = Ec2InstanceConfig(instances=[])
        mock_load.return_value = mock_config
        
        ec2_instance.create_resource(
            account_id="123456789",
            region="us-east-1",
            module="ec2",
            sub_module="instances"
        )
        
        mock_create.assert_not_called()
        mock_export.assert_called_once_with("instances", {})
    
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_merges_multiple_instance_outputs(self, mock_load, mock_create, mock_export):
        instances = [
            Ec2InstanceResource(
                name=f"instance{i}",
                ami=f"ami-{i}",
                instance_type="t2.micro",
                key_name="key",
                strict_validation=False,
            )
            for i in range(3)
        ]
        
        mock_config = Ec2InstanceConfig(instances=instances)
        mock_load.return_value = mock_config
        
        mock_create.side_effect = [
            {"instance0": {"instance_id": "i-000"}},
            {"instance1": {"instance_id": "i-111"}},
            {"instance2": {"instance_id": "i-222"}}
        ]
        
        ec2_instance.create_resource(
            account_id="123456789",
            region="us-east-1",
            module="ec2",
            sub_module="instances"
        )
        
        expected_outputs = {
            "instance0": {"instance_id": "i-000"},
            "instance1": {"instance_id": "i-111"},
            "instance2": {"instance_id": "i-222"}
        }
        
        mock_export.assert_called_once_with("instances", expected_outputs)
    
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_with_different_account_ids(self, mock_load, mock_create, mock_export):
        mock_config = Ec2InstanceConfig(instances=[])
        mock_load.return_value = mock_config
        mock_create.return_value = {}
        
        ec2_instance.create_resource(
            account_id="999888777",
            region="us-west-2",
            module="compute",
            sub_module="web-servers"
        )
        
        mock_load.assert_called_once_with(
            config_path="configs/999888777/us-west-2/compute/web-servers",
            model_class=Ec2InstanceConfig
        )
    
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_with_different_regions(self, mock_load, mock_create, mock_export):
        mock_config = Ec2InstanceConfig(instances=[])
        mock_load.return_value = mock_config
        mock_create.return_value = {}
        
        regions = ["us-east-1", "us-west-2", "eu-central-1", "ap-south-1"]
        
        for region in regions:
            ec2_instance.create_resource(
                account_id="123456789",
                region=region,
                module="ec2",
                sub_module="instances"
            )
        
        assert mock_load.call_count == len(regions)


class TestCreateResourceEdgeCases:
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_handles_config_load_failure(self, mock_load, mock_create, mock_export):
        mock_load.side_effect = Exception("Config load failed")
        
        with pytest.raises(Exception) as exc_info:
            ec2_instance.create_resource(
                account_id="123456789",
                region="us-east-1",
                module="ec2",
                sub_module="instances"
            )
        
        assert "Config load failed" in str(exc_info.value)
        mock_create.assert_not_called()
        mock_export.assert_not_called()
    
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_handles_instance_creation_failure(self, mock_load, mock_create, mock_export):
        instance = Ec2InstanceResource(
            name="test",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        
        mock_config = Ec2InstanceConfig(instances=[instance])
        mock_load.return_value = mock_config
        mock_create.side_effect = Exception("Instance creation failed")
        
        with pytest.raises(Exception) as exc_info:
            ec2_instance.create_resource(
                account_id="123456789",
                region="us-east-1",
                module="ec2",
                sub_module="instances"
            )
        
        assert "Instance creation failed" in str(exc_info.value)
    
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_with_special_characters_in_path(self, mock_load, mock_create, mock_export):
        mock_config = Ec2InstanceConfig(instances=[])
        mock_load.return_value = mock_config
        mock_create.return_value = {}
        
        ec2_instance.create_resource(
            account_id="123-456-789",
            region="us-east-1",
            module="ec2-compute",
            sub_module="web_servers"
        )
        
        mock_load.assert_called_once_with(
            config_path="configs/123-456-789/us-east-1/ec2-compute/web_servers",
            model_class=Ec2InstanceConfig
        )
    
    @patch('modules.ec2_instance.pulumi.export')
    @patch('modules.ec2_instance.create')
    @patch('modules.ec2_instance.ConfigProvider.load')
    def test_create_resource_with_single_instance(self, mock_load, mock_create, mock_export):
        instance = Ec2InstanceResource(
            name="single",
            ami="ami-123",
            instance_type="t2.micro",
            key_name="key",
            strict_validation=False,
        )
        
        mock_config = Ec2InstanceConfig(instances=[instance])
        mock_load.return_value = mock_config
        
        mock_create.return_value = {
            "single": {
                "instance_id": "i-single",
                "public_ip": "10.0.0.1",
                "security_group_ids": []
            }
        }
        
        ec2_instance.create_resource(
            account_id="123456789",
            region="us-east-1",
            module="ec2",
            sub_module="instances"
        )
        
        mock_create.assert_called_once()
        mock_export.assert_called_once()
        
        exported_data = mock_export.call_args[0][1]
        assert "single" in exported_data
        assert exported_data["single"]["instance_id"] == "i-single"
