import pytest
from pydantic import ValidationError
from models.base.base_resource import BaseResource, Resource, TAG_VALIDATIONS
from models.constants.constants import Environment, CostCentre, Team


class TestResource:
    def test_resource_creation_with_defaults(self):
        resource = BaseResource(
            name="test-resource",
            tags={
                "Environment": Environment.DEV.value,
                "Cost_centre": CostCentre.ENGINEERING.value,
                "Team": Team.SRE.value,
            },
        )
        assert resource.name == "test-resource"
        assert resource.strict_validation is True
    
    def test_resource_creation_with_custom_tags(self):
        tags = {
            "key1": "value1",
            "key2": "value2",
            "Environment": Environment.DEV.value,
            "Cost_centre": CostCentre.ENGINEERING.value,
            "Team": Team.SRE.value,
        }
        resource = BaseResource(name="test", tags=tags)
        assert "key1" in resource.tags
        assert resource.tags["key1"] == "value1"
    
    def test_resource_strict_validation_can_be_disabled(self):
        resource = BaseResource(name="test", strict_validation=False)
        assert resource.strict_validation is False


class TestBaseResourceNameValidation:
    def test_name_normalization_strips_whitespace(self):
        resource = BaseResource(
            name="  test-resource  ",
            strict_validation=False,
        )
        assert resource.name == "test-resource"
    
    def test_name_normalization_converts_to_lowercase(self):
        resource = BaseResource(
            name="TEST-Resource",
            strict_validation=False,
        )
        assert resource.name == "test-resource"
    
    def test_name_normalization_replaces_underscores_with_hyphens(self):
        resource = BaseResource(
            name="test_resource_name",
            strict_validation=False,
        )
        assert resource.name == "test-resource-name"
    
    def test_name_normalization_combined(self):
        resource = BaseResource(
            name="  TEST_Resource_Name  ",
            strict_validation=False,
        )
        assert resource.name == "test-resource-name"
    
    def test_valid_name_with_alphanumeric_and_hyphens(self):
        resource = BaseResource(
            name="valid-name-123",
            strict_validation=False,
        )
        assert resource.name == "valid-name-123"
    
    def test_invalid_name_with_special_characters_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            BaseResource(name="invalid@name", strict_validation=False)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "invalid_name"
    
    def test_invalid_name_with_spaces_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            BaseResource(name="invalid name", strict_validation=False)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "invalid_name"
    
    def test_invalid_name_exceeding_max_length_raises_error(self):
        long_name = "a" * 64
        with pytest.raises(ValidationError) as exc_info:
            BaseResource(name=long_name, strict_validation=False)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "invalid_name_length"
    
    def test_valid_name_at_max_length(self):
        max_length_name = "a" * 63
        resource = BaseResource(
            name=max_length_name,
            strict_validation=False,
        )
        assert len(resource.name) == 63


@pytest.mark.parametrize(
    "invalid_name",
    [
        "name!",
        "name@test",
        "name#123",
        "name$",
        "name%",
        "name^",
        "name&",
        "name*",
        "name()",
        "name+",
        "name=",
        "name[",
        "name]",
        "name{",
        "name}",
        "name|",
        "name\\",
        "name/",
        "name?",
        "name<",
        "name>",
        "name,",
        "name.",
        "name;",
        "name:",
        "name'",
        'name"',
        "name`",
        "name~",
    ],
)
def test_invalid_names_with_various_special_characters(invalid_name):
    with pytest.raises(ValidationError) as exc_info:
        BaseResource(name=invalid_name, strict_validation=False)
    
    errors = exc_info.value.errors()
    assert errors[0]["type"] == "invalid_name"


class TestBaseResourcePostInit:
    def test_post_init_adds_name_tag_when_missing(self):
        resource = BaseResource(
            name="test-resource",
            strict_validation=False,
        )
        assert resource.tags["Name"] == "test-resource"
    
    def test_post_init_preserves_existing_name_tag(self):
        resource = BaseResource(
            name="test-resource",
            tags={"Name": "custom-name"},
            strict_validation=False,
        )
        assert resource.tags["Name"] == "custom-name"
    
    def test_post_init_adds_created_by_tag(self):
        resource = BaseResource(
            name="test-resource",
            strict_validation=False,
        )
        assert resource.tags["Created_by"] == "pulumi"
    
    def test_post_init_overwrites_created_by_tag(self):
        resource = BaseResource(
            name="test-resource",
            tags={"Created_by": "manual"},
            strict_validation=False,
        )
        assert resource.tags["Created_by"] == "pulumi"


class TestBaseResourceTagValidations:
    def test_strict_validation_requires_environment_tag(self):
        with pytest.raises(ValidationError) as exc_info:
            BaseResource(
                name="test",
                tags={
                    "Cost_centre": CostCentre.ENGINEERING.value,
                    "Team": Team.SRE.value,
                },
            )
        
        errors = exc_info.value.errors()
        assert any(e["type"] == "missing_environment" for e in errors)
    
    def test_strict_validation_requires_cost_centre_tag(self):
        with pytest.raises(ValidationError) as exc_info:
            BaseResource(
                name="test",
                tags={
                    "Environment": Environment.DEV.value,
                    "Team": Team.SRE.value,
                },
            )
        
        errors = exc_info.value.errors()
        assert any(e["type"] == "missing_cost_centre" for e in errors)
    
    def test_strict_validation_requires_team_tag(self):
        with pytest.raises(ValidationError) as exc_info:
            BaseResource(
                name="test",
                tags={
                    "Environment": Environment.DEV.value,
                    "Cost_centre": CostCentre.ENGINEERING.value,
                },
            )
        
        errors = exc_info.value.errors()
        assert any(e["type"] == "missing_team" for e in errors)
    
    def test_strict_validation_with_all_required_tags_succeeds(self):
        resource = BaseResource(
            name="test",
            tags={
                "Environment": Environment.DEV.value,
                "Cost_centre": CostCentre.ENGINEERING.value,
                "Team": Team.SRE.value,
            },
        )
        assert resource.name == "test"
    
    def test_strict_validation_rejects_invalid_environment_value(self):
        with pytest.raises(ValidationError) as exc_info:
            BaseResource(
                name="test",
                tags={
                    "Environment": "invalid",
                    "Cost_centre": CostCentre.ENGINEERING.value,
                    "Team": Team.SRE.value,
                },
            )
        
        errors = exc_info.value.errors()
        assert any(e["type"] == "invalid_environment" for e in errors)
    
    def test_strict_validation_rejects_invalid_cost_centre_value(self):
        with pytest.raises(ValidationError) as exc_info:
            BaseResource(
                name="test",
                tags={
                    "Environment": Environment.DEV.value,
                    "Cost_centre": "invalid",
                    "Team": Team.SRE.value,
                },
            )
        
        errors = exc_info.value.errors()
        assert any(e["type"] == "invalid_cost_centre" for e in errors)
    
    def test_strict_validation_rejects_invalid_team_value(self):
        with pytest.raises(ValidationError) as exc_info:
            BaseResource(
                name="test",
                tags={
                    "Environment": Environment.DEV.value,
                    "Cost_centre": CostCentre.ENGINEERING.value,
                    "Team": "invalid",
                },
            )
        
        errors = exc_info.value.errors()
        assert any(e["type"] == "invalid_team" for e in errors)
    
    def test_strict_validation_disabled_allows_missing_tags(self):
        resource = BaseResource(
            name="test",
            strict_validation=False,
        )
        assert resource.name == "test"
    
    def test_strict_validation_disabled_allows_invalid_tag_values(self):
        resource = BaseResource(
            name="test",
            tags={
                "Environment": "invalid",
                "Cost_centre": "invalid",
                "Team": "invalid",
            },
            strict_validation=False,
        )
        assert resource.name == "test"


class TestBaseResourceMethods:
    def test_get_pulumi_dict_returns_model_dump(self):
        resource = BaseResource(
            name="test",
            tags={
                "Environment": Environment.DEV.value,
                "Cost_centre": CostCentre.ENGINEERING.value,
                "Team": Team.SRE.value,
            },
        )
        pulumi_dict = resource.get_pulumi_dict()
        
        assert isinstance(pulumi_dict, dict)
        assert pulumi_dict["name"] == "test"
        assert "tags" in pulumi_dict
        assert "strict_validation" not in pulumi_dict
    
    def test_resource_name_property(self):
        resource = BaseResource(
            name="test-resource",
            strict_validation=False,
        )
        assert resource.resource_name == "test-resource"
    
    def test_resource_name_property_returns_normalized_name(self):
        resource = BaseResource(
            name="TEST_Resource",
            strict_validation=False,
        )
        assert resource.resource_name == "test-resource"


class TestTagValidationsConstant:
    def test_tag_validations_contains_environment(self):
        assert "Environment" in TAG_VALIDATIONS
        assert TAG_VALIDATIONS["Environment"] == Environment
    
    def test_tag_validations_contains_cost_centre(self):
        assert "Cost_centre" in TAG_VALIDATIONS
        assert TAG_VALIDATIONS["Cost_centre"] == CostCentre
    
    def test_tag_validations_contains_team(self):
        assert "Team" in TAG_VALIDATIONS
        assert TAG_VALIDATIONS["Team"] == Team
    
    def test_tag_validations_has_exactly_three_entries(self):
        assert len(TAG_VALIDATIONS) == 3


class TestBaseResourceEdgeCases:
    def test_empty_name_after_normalization_raises_error(self):
        with pytest.raises(ValidationError):
            BaseResource(name="   ", strict_validation=False)
    
    def test_name_with_only_hyphens_is_valid(self):
        resource = BaseResource(name="---", strict_validation=False)
        assert resource.name == "---"
    
    def test_name_with_numbers_only_is_valid(self):
        resource = BaseResource(name="12345", strict_validation=False)
        assert resource.name == "12345"
    
    def test_tags_can_contain_additional_custom_tags(self):
        resource = BaseResource(
            name="test",
            tags={
                "Environment": Environment.DEV.value,
                "Cost_centre": CostCentre.ENGINEERING.value,
                "Team": Team.SRE.value,
                "CustomTag": "custom-value",
                "AnotherTag": "another-value",
            },
        )
        assert resource.tags["CustomTag"] == "custom-value"
        assert resource.tags["AnotherTag"] == "another-value"
    
    def test_empty_tags_dict_with_strict_validation_disabled(self):
        resource = BaseResource(
            name="test",
            tags={},
            strict_validation=False,
        )
        assert "Name" in resource.tags
        assert "Created_by" in resource.tags
