import pytest
from models.constants.constants import (
    Environment,
    CostCentre,
    Team,
    AWSRegion,
    LowercaseStrEnum,
    AWS_NAME_REGEX,
    AWS_NAME_MAX_LENGTH,
)


def test_aws_name_regex_constant():
    assert AWS_NAME_REGEX == r"^[a-zA-Z0-9-]+$"


def test_aws_name_max_length_constant():
    assert AWS_NAME_MAX_LENGTH == 63


def test_lowercase_str_enum_generates_lowercase_values():
    class TestEnum(LowercaseStrEnum):
        TEST_VALUE = "test_value"
        ANOTHER_VALUE = "another_value"
    
    assert TestEnum.TEST_VALUE.value == "test_value"
    assert TestEnum.ANOTHER_VALUE.value == "another_value"


class TestEnvironmentEnum:
    def test_environment_has_dev(self):
        assert Environment.DEV.value == "dev"
    
    def test_environment_has_prod(self):
        assert Environment.PROD.value == "prod"
    
    def test_environment_has_stage(self):
        assert Environment.STAGE.value == "stage"
    
    def test_environment_all_values(self):
        expected_values = {"dev", "prod", "stage"}
        actual_values = {e.value for e in Environment}
        assert actual_values == expected_values
    
    def test_environment_string_representation(self):
        assert str(Environment.DEV) == "dev"


class TestCostCentreEnum:
    def test_cost_centre_has_engineering(self):
        assert CostCentre.ENGINEERING.value == "engineering"
    
    def test_cost_centre_has_bi(self):
        assert CostCentre.BI.value == "bi"
    
    def test_cost_centre_has_infra(self):
        assert CostCentre.INFRA.value == "infra"
    
    def test_cost_centre_all_values(self):
        expected_values = {"engineering", "bi", "infra"}
        actual_values = {c.value for c in CostCentre}
        assert actual_values == expected_values


class TestTeamEnum:
    def test_team_has_sre(self):
        assert Team.SRE.value == "sre"
    
    def test_team_has_data_platform(self):
        assert Team.DATA_PLATFORM.value == "data_platform"
    
    def test_team_has_data_science(self):
        assert Team.DATA_SCIENCE.value == "data_science"
    
    def test_team_has_backend(self):
        assert Team.BACKEND.value == "backend"
    
    def test_team_has_web(self):
        assert Team.WEB.value == "web"
    
    def test_team_has_android(self):
        assert Team.ANDROID.value == "android"
    
    def test_team_has_qa(self):
        assert Team.QA.value == "qa"
    
    def test_team_all_values(self):
        expected_values = {
            "sre",
            "data_platform",
            "data_science",
            "backend",
            "web",
            "android",
            "qa",
        }
        actual_values = {t.value for t in Team}
        assert actual_values == expected_values


class TestAWSRegionEnum:
    def test_aws_region_us_east_1(self):
        assert AWSRegion.US_EAST_1 == "us-east-1"
        assert AWSRegion.US_EAST_1.value == "us-east-1"
    
    def test_aws_region_us_east_2(self):
        assert AWSRegion.US_EAST_2 == "us-east-2"
    
    def test_aws_region_us_west_1(self):
        assert AWSRegion.US_WEST_1 == "us-west-1"
    
    def test_aws_region_us_west_2(self):
        assert AWSRegion.US_WEST_2 == "us-west-2"
    
    def test_aws_region_eu_central_1(self):
        assert AWSRegion.EU_CENTRAL_1 == "eu-central-1"
    
    def test_aws_region_ap_south_1(self):
        assert AWSRegion.AP_SOUTH_1 == "ap-south-1"
    
    def test_aws_region_string_representation(self):
        assert str(AWSRegion.US_EAST_1) == "us-east-1"
        assert str(AWSRegion.EU_WEST_1) == "eu-west-1"
    
    def test_aws_region_count(self):
        assert len(list(AWSRegion)) == 24


@pytest.mark.parametrize(
    "region",
    [
        AWSRegion.US_EAST_1,
        AWSRegion.US_EAST_2,
        AWSRegion.US_WEST_1,
        AWSRegion.US_WEST_2,
        AWSRegion.AF_SOUTH_1,
        AWSRegion.AP_EAST_1,
        AWSRegion.AP_SOUTH_1,
        AWSRegion.AP_NORTHEAST_1,
        AWSRegion.AP_NORTHEAST_2,
        AWSRegion.AP_NORTHEAST_3,
        AWSRegion.AP_SOUTHEAST_1,
        AWSRegion.AP_SOUTHEAST_2,
        AWSRegion.AP_SOUTHEAST_3,
        AWSRegion.CA_CENTRAL_1,
        AWSRegion.EU_CENTRAL_1,
        AWSRegion.EU_WEST_1,
        AWSRegion.EU_WEST_2,
        AWSRegion.EU_WEST_3,
        AWSRegion.EU_NORTH_1,
        AWSRegion.EU_SOUTH_1,
        AWSRegion.EU_SOUTH_2,
        AWSRegion.ME_SOUTH_1,
        AWSRegion.ME_CENTRAL_1,
        AWSRegion.SA_EAST_1,
    ],
)
def test_aws_region_all_regions_are_valid_strings(region):
    assert isinstance(region.value, str)
    assert len(region.value) > 0
    assert "-" in region.value
