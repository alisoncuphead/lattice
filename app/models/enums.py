from enum import Enum


class InfrastructureType(str, Enum):
    IP = "ip"
    DOMAIN = "domain"
    ASN = "asn"
    CIDR = "cidr"
    URL = "url"


class ActorType(str, Enum):
    NATION_STATE = "nation_state"
    CYBERCRIME = "cybercrime"
    HACKTIVISM = "hacktivism"
    INSIDER_THREAT = "insider_threat"
    UNKNOWN = "unknown"


class CapabilityType(str, Enum):
    TOOLKIT = "toolkit"
    EXPLOIT = "exploit"
    WEB_SHELL = "web_shell"
    COMMAND_AND_CONTROL = "c2_framework"
    TTP = "ttp"


class WorkspaceStatus(str, Enum):
    PRODUCTION = "production"
    WORKSPACE = "workspace"
