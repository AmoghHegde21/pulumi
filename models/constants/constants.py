from enum import StrEnum, auto

AWS_NAME_REGEX = r"^[a-zA-Z0-9-]+$"
AWS_NAME_MAX_LENGTH = 63


class LowercaseStrEnum(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()


class Environment(LowercaseStrEnum):
    DEV = auto()
    PROD = auto()
    STAGE = auto()


class CostCentre(LowercaseStrEnum):
    ENGINEERING = auto()
    BI = auto()
    INFRA = auto()


class Team(LowercaseStrEnum):
    SRE = auto()
    DATA_PLATFORM = auto()
    DATA_SCIENCE = auto()
    BACKEND = auto()
    WEB = auto()
    ANDROID = auto()
    QA = auto()


class AWSRegion(StrEnum):
    """Enum for AWS regions.

    Attributes:
        US_EAST_1: US East (N. Virginia)
        US_EAST_2: US East (Ohio)
        US_WEST_1: US West (N. California)
        US_WEST_2: US West (Oregon)
        AF_SOUTH_1: Africa (Cape Town)
        AP_EAST_1: Asia Pacific (Hong Kong)
        AP_SOUTH_1: Asia Pacific (Mumbai)
        AP_NORTHEAST_1: Asia Pacific (Tokyo)
        AP_NORTHEAST_2: Asia Pacific (Seoul)
        AP_NORTHEAST_3: Asia Pacific (Osaka)
        AP_SOUTHEAST_1: Asia Pacific (Singapore)
        AP_SOUTHEAST_2: Asia Pacific (Sydney)
        AP_SOUTHEAST_3: Asia Pacific (Jakarta)
        CA_CENTRAL_1: Canada (Central)
        EU_CENTRAL_1: Europe (Frankfurt)
        EU_WEST_1: Europe (Ireland)
        EU_WEST_2: Europe (London)
        EU_WEST_3: Europe (Paris)
        EU_NORTH_1: Europe (Stockholm)
        EU_SOUTH_1: Europe (Milan)
        EU_SOUTH_2: Europe (Spain)
        ME_SOUTH_1: Middle East (Bahrain)
        ME_CENTRAL_1: Middle East (UAE)
        SA_EAST_1: South America (São Paulo)
    """

    US_EAST_1 = "us-east-1"
    US_EAST_2 = "us-east-2"
    US_WEST_1 = "us-west-1"
    US_WEST_2 = "us-west-2"
    AF_SOUTH_1 = "af-south-1"
    AP_EAST_1 = "ap-east-1"
    AP_SOUTH_1 = "ap-south-1"
    AP_NORTHEAST_1 = "ap-northeast-1"
    AP_NORTHEAST_2 = "ap-northeast-2"
    AP_NORTHEAST_3 = "ap-northeast-3"
    AP_SOUTHEAST_1 = "ap-southeast-1"
    AP_SOUTHEAST_2 = "ap-southeast-2"
    AP_SOUTHEAST_3 = "ap-southeast-3"
    CA_CENTRAL_1 = "ca-central-1"
    EU_CENTRAL_1 = "eu-central-1"
    EU_WEST_1 = "eu-west-1"
    EU_WEST_2 = "eu-west-2"
    EU_WEST_3 = "eu-west-3"
    EU_NORTH_1 = "eu-north-1"
    EU_SOUTH_1 = "eu-south-1"
    EU_SOUTH_2 = "eu-south-2"
    ME_SOUTH_1 = "me-south-1"
    ME_CENTRAL_1 = "me-central-1"
    SA_EAST_1 = "sa-east-1"

    def __str__(self) -> str:
        return self.value
