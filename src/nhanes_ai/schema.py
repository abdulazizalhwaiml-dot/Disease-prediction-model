"""Shared training/inference contracts and explicit study label definitions."""

from dataclasses import asdict, dataclass

SCHEMA_VERSION = 3
AGE_MIN, AGE_MAX = 20, 79
# Separate earlier/later cycles within each era; never tune using test outcomes.
PARTITIONS = {
    "development": ["1999-2000", "2011-2012", "2013-2014"],
    "validation": ["2001-2002", "2015-2016"],
    "test": ["2003-2004", "2005-2006", "2017-2018"],
}
USER_FIELDS = [
    "age",
    "gender",
    "height_cm",
    "weight_kg",
    "waist_cm",
    "body_fat_pct",
    "family_diabetes",
    "family_heart_early",
]
FAMILY_FIELDS = ["family_diabetes", "family_heart_early"]
NUMERIC = [
    "gender",
    "age",
    "waist_cm",
    "weight_kg",
    "height_cm",
    "bmi",
    "body_fat_pct",
    "fat_mass_kg",
    "fat_free_mass_kg",
]
FEATURES = NUMERIC + FAMILY_FIELDS
DISEASES = {
    "high_cholesterol": "High cholesterol",
    "high_blood_pressure": "High blood pressure",
    "diabetes": "Diabetes",
    "coronary_artery_disease": "Coronary artery disease",
    "heart_attack": "Heart attack",
    "angina": "Angina",
    "heart_failure": "Congestive heart failure",
    "stroke": "Stroke",
}
CARDIAC_LABELS = {
    "coronary_artery_disease": "MCQ160C",
    "heart_attack": "MCQ160E",
    "angina": "MCQ160D",
    "heart_failure": "MCQ160B",
    "stroke": "MCQ160F",
}


@dataclass(frozen=True)
class LabelConfig:
    """Operational study thresholds, configurable independently of the feature pipeline."""

    non_hdl_mg_dl: float = 190.0
    systolic_mm_hg: float = 140.0
    diastolic_mm_hg: float = 90.0
    hba1c_pct: float = 6.5

    def to_dict(self):
        return asdict(self)
