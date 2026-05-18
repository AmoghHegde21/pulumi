import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pydantic import BaseModel
from provider.config_provider import ConfigProvider


class SampleModel(BaseModel):
    name: str
    value: int


class SampleListModel(BaseModel):
    items: list[str]


class ComplexModel(BaseModel):
    items: list[str] = []
    config: dict[str, str] = {}
    name: str = "default"


class TestConfigProvider:
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open, read_data="name: test\nvalue: 42\n")
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_single_yaml_file(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = ["/fake/base/configs/test/config.yaml"]
        mock_yaml_load.return_value = {"name": "test", "value": 42}
        
        result = ConfigProvider.load(
            config_path="configs/test",
            model_class=SampleModel
        )
        
        assert result.name == "test"
        assert result.value == 42
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_multiple_yaml_files_with_lists(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = [
            "/fake/base/configs/test/config1.yaml",
            "/fake/base/configs/test/config2.yaml"
        ]
        mock_yaml_load.side_effect = [
            {"items": ["item1", "item2"]},
            {"items": ["item3", "item4"]}
        ]
        
        result = ConfigProvider.load(
            config_path="configs/test",
            model_class=SampleListModel
        )
        
        assert len(result.items) == 4
        assert "item1" in result.items
        assert "item4" in result.items
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_merges_lists_from_multiple_files(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = [
            "/fake/base/configs/test/config1.yaml",
            "/fake/base/configs/test/config2.yaml"
        ]
        mock_yaml_load.side_effect = [
            {"items": ["a", "b"], "name": "first"},
            {"items": ["c", "d"]}
        ]
        
        result = ConfigProvider.load(
            config_path="configs/test",
            model_class=ComplexModel
        )
        
        assert len(result.items) == 4
        assert result.items == ["a", "b", "c", "d"]
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_merges_dicts_from_multiple_files(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = [
            "/fake/base/configs/test/config1.yaml",
            "/fake/base/configs/test/config2.yaml"
        ]
        mock_yaml_load.side_effect = [
            {"config": {"x": "1", "y": "2"}},
            {"config": {"z": "3"}}
        ]
        
        result = ConfigProvider.load(
            config_path="configs/test",
            model_class=ComplexModel
        )
        
        assert len(result.config) == 3
        assert result.config["x"] == "1"
        assert result.config["z"] == "3"
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    def test_load_empty_directory(self, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = []
        
        with pytest.raises(Exception):
            ConfigProvider.load(
                config_path="configs/empty",
                model_class=SampleModel
            )
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_scalar_values_use_last_file(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = [
            "/fake/base/configs/test/config1.yaml",
            "/fake/base/configs/test/config2.yaml"
        ]
        mock_yaml_load.side_effect = [
            {"name": "first"},
            {"name": "second"}
        ]
        
        result = ConfigProvider.load(
            config_path="configs/test",
            model_class=ComplexModel
        )
        
        assert result.name == "second"
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_handles_yaml_with_empty_values(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = ["/fake/base/configs/test/config.yaml"]
        mock_yaml_load.return_value = {"items": [], "config": {}, "name": "test"}
        
        result = ConfigProvider.load(
            config_path="configs/test",
            model_class=ComplexModel
        )
        
        assert result.items == []
        assert result.config == {}
        assert result.name == "test"
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_with_nested_path(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = ["/fake/base/configs/account1/us-east-1/ec2/instances/config.yaml"]
        mock_yaml_load.return_value = {"name": "nested", "value": 100}
        
        result = ConfigProvider.load(
            config_path="configs/account1/us-east-1/ec2/instances",
            model_class=SampleModel
        )
        
        assert result.name == "nested"
        assert result.value == 100


class TestConfigProviderEdgeCases:
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_with_invalid_yaml_syntax(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = ["/fake/base/configs/test/bad.yaml"]
        mock_yaml_load.side_effect = Exception("Invalid YAML")
        
        with pytest.raises(Exception):
            ConfigProvider.load(
                config_path="configs/test",
                model_class=SampleModel
            )
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_with_missing_required_fields(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = ["/fake/base/configs/test/incomplete.yaml"]
        mock_yaml_load.return_value = {"name": "test"}
        
        with pytest.raises(Exception):
            ConfigProvider.load(
                config_path="configs/test",
                model_class=SampleModel
            )
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_with_wrong_data_types(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = ["/fake/base/configs/test/wrong_type.yaml"]
        mock_yaml_load.return_value = {"name": "test", "value": "not_a_number"}
        
        with pytest.raises(Exception):
            ConfigProvider.load(
                config_path="configs/test",
                model_class=SampleModel
            )
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_with_multiple_yaml_files_in_order(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = [
            f"/fake/base/configs/test/config{i}.yaml" for i in range(5)
        ]
        mock_yaml_load.side_effect = [
            {"items": [f"item{i}"]} for i in range(5)
        ]
        
        result = ConfigProvider.load(
            config_path="configs/test",
            model_class=SampleListModel
        )
        
        assert len(result.items) == 5
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_dict_update_overwrites_keys(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = [
            "/fake/base/configs/test/config1.yaml",
            "/fake/base/configs/test/config2.yaml"
        ]
        mock_yaml_load.side_effect = [
            {"config": {"key1": "original"}},
            {"config": {"key1": "updated"}}
        ]
        
        result = ConfigProvider.load(
            config_path="configs/test",
            model_class=ComplexModel
        )
        
        assert result.config["key1"] == "updated"
    
    @patch('provider.config_provider.glob.glob')
    @patch('provider.config_provider.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('provider.config_provider.yaml.safe_load')
    def test_load_handles_none_from_yaml(self, mock_yaml_load, mock_file, mock_path, mock_glob):
        mock_path.return_value.resolve.return_value.parent.parent = "/fake/base"
        mock_glob.return_value = ["/fake/base/configs/test/empty.yaml"]
        mock_yaml_load.return_value = None
        
        with pytest.raises(Exception):
            ConfigProvider.load(
                config_path="configs/test",
                model_class=SampleModel
            )
