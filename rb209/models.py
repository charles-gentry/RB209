"""Data models for RB209 fertiliser recommendations."""

from dataclasses import dataclass, field
from enum import Enum


class SoilType(Enum):
    """Soil texture categories for SNS and lime calculations."""
    LIGHT = "light"        # Sandy, shallow soils
    MEDIUM = "medium"      # Loamy soils
    HEAVY = "heavy"        # Clay, deep soils
    ORGANIC = "organic"    # Peaty, organic soils


class CropCategory(Enum):
    """Broad crop grouping."""
    ARABLE = "arable"
    GRASSLAND = "grassland"
    POTATOES = "potatoes"


class Crop(Enum):
    """All supported crops."""
    # Cereals
    WINTER_WHEAT_FEED = "winter-wheat-feed"
    WINTER_WHEAT_MILLING = "winter-wheat-milling"
    SPRING_WHEAT = "spring-wheat"
    WINTER_BARLEY = "winter-barley"
    SPRING_BARLEY = "spring-barley"
    WINTER_OATS = "winter-oats"
    SPRING_OATS = "spring-oats"
    WINTER_RYE = "winter-rye"
    # Oilseeds
    WINTER_OILSEED_RAPE = "winter-oilseed-rape"
    SPRING_OILSEED_RAPE = "spring-oilseed-rape"
    LINSEED = "linseed"
    # Pulses
    PEAS = "peas"
    FIELD_BEANS = "field-beans"
    # Root/forage
    SUGAR_BEET = "sugar-beet"
    FORAGE_MAIZE = "forage-maize"
    # Potatoes
    POTATOES_MAINCROP = "potatoes-maincrop"
    POTATOES_EARLY = "potatoes-early"
    POTATOES_SEED = "potatoes-seed"
    # Grassland
    GRASS_GRAZED = "grass-grazed"
    GRASS_SILAGE = "grass-silage"
    GRASS_HAY = "grass-hay"
    GRASS_GRAZED_ONE_CUT = "grass-grazed-one-cut"


class PreviousCrop(Enum):
    """Previous crop categories for SNS determination."""
    CEREALS = "cereals"
    OILSEED_RAPE = "oilseed-rape"
    POTATOES = "potatoes"
    SUGAR_BEET = "sugar-beet"
    PEAS_BEANS = "peas-beans"
    LINSEED = "linseed"
    FORAGE_MAIZE = "forage-maize"
    SET_ASIDE = "set-aside"
    GRASS_1_2_YEAR = "grass-1-2yr"
    GRASS_3_5_YEAR = "grass-3-5yr"
    GRASS_LONG_TERM = "grass-long-term"
    VEGETABLES = "vegetables"
    FALLOW = "fallow"


class OrganicMaterial(Enum):
    """Organic material types."""
    CATTLE_FYM = "cattle-fym"
    PIG_FYM = "pig-fym"
    SHEEP_FYM = "sheep-fym"
    HORSE_FYM = "horse-fym"
    POULTRY_LITTER = "poultry-litter"
    LAYER_MANURE = "layer-manure"
    CATTLE_SLURRY = "cattle-slurry"
    PIG_SLURRY = "pig-slurry"
    GREEN_COMPOST = "green-compost"
    GREEN_FOOD_COMPOST = "green-food-compost"
    BIOSOLIDS_CAKE = "biosolids-cake"
    PAPER_CRUMBLE = "paper-crumble"


class Rainfall(Enum):
    """Excess winter rainfall categories."""
    LOW = "low"        # <150 mm
    MEDIUM = "medium"  # 150-250 mm
    HIGH = "high"      # >250 mm


# Mapping of previous crops to N-residue categories for SNS lookup
class NResidueCategory(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very-high"


PREVIOUS_CROP_N_CATEGORY: dict[PreviousCrop, NResidueCategory] = {
    PreviousCrop.CEREALS: NResidueCategory.LOW,
    PreviousCrop.SUGAR_BEET: NResidueCategory.LOW,
    PreviousCrop.LINSEED: NResidueCategory.LOW,
    PreviousCrop.FORAGE_MAIZE: NResidueCategory.LOW,
    PreviousCrop.SET_ASIDE: NResidueCategory.LOW,
    PreviousCrop.FALLOW: NResidueCategory.LOW,
    PreviousCrop.OILSEED_RAPE: NResidueCategory.MEDIUM,
    PreviousCrop.POTATOES: NResidueCategory.MEDIUM,
    PreviousCrop.PEAS_BEANS: NResidueCategory.HIGH,
    PreviousCrop.VEGETABLES: NResidueCategory.HIGH,
    PreviousCrop.GRASS_1_2_YEAR: NResidueCategory.HIGH,
    PreviousCrop.GRASS_3_5_YEAR: NResidueCategory.HIGH,
    PreviousCrop.GRASS_LONG_TERM: NResidueCategory.VERY_HIGH,
}


@dataclass
class NutrientRecommendation:
    """Full nutrient recommendation for a crop."""
    crop: str
    nitrogen: float       # kg N/ha
    phosphorus: float     # kg P2O5/ha
    potassium: float      # kg K2O/ha
    magnesium: float      # kg MgO/ha
    sulfur: float         # kg SO3/ha
    notes: list[str] = field(default_factory=list)


@dataclass
class OrganicNutrients:
    """Nutrients supplied by an organic material application."""
    material: str
    rate: float            # t/ha or m3/ha
    unit: str              # "t" or "m3"
    total_n: float         # kg/ha
    available_n: float     # kg/ha (crop-available in year 1)
    p2o5: float            # kg/ha
    k2o: float             # kg/ha
    mgo: float             # kg/ha
    so3: float             # kg/ha
    notes: list[str] = field(default_factory=list)


@dataclass
class LimeRecommendation:
    """Lime requirement result."""
    current_ph: float
    target_ph: float
    soil_type: str
    lime_required: float   # t CaCO3/ha
    notes: list[str] = field(default_factory=list)


@dataclass
class SNSResult:
    """Soil Nitrogen Supply calculation result."""
    sns_index: int
    previous_crop: str = ""
    soil_type: str = ""
    rainfall: str = ""
    method: str = "field-assessment"
    smn: float | None = None
    crop_n: float | None = None
    sns_value: float | None = None
    notes: list[str] = field(default_factory=list)
