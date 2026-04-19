from enum import Enum


class BloodType(str, Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class BloodComponent(str, Enum):
    WHOLE_BLOOD = "whole_blood"
    PACKED_RED_CELLS = "packed_red_cells"
    PLASMA = "plasma"
    PLATELETS = "platelets"
    CRYOPRECIPITATE = "cryoprecipitate"


class BloodBagStatus(str, Enum):
    COLLECTED = "collected"
    TESTED = "tested"
    AVAILABLE = "available"
    RESERVED = "reserved"
    ISSUED = "issued"
    TRANSFUSED = "transfused"
    DISCARDED = "discarded"
    EXPIRED = "expired"


class RequestUrgency(str, Enum):
    ROUTINE = "routine"
    URGENT = "urgent"
    CRITICAL = "critical"


class RequestStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    DONOR = "donor"
    ADMIN = "admin"
    HOSPITAL = "hospital"


class DegradedStateSource(str, Enum):
    DONOR_IMPACT = "donor_impact"
    INVENTORY = "inventory"
    URGENT_ROUTING = "urgent_routing"


class DegradedState(str, Enum):
    DEGRADED = "degraded"
    RECOVERED = "recovered"
