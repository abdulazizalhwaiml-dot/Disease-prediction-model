"""Serializable preprocessing shared verbatim by training and inference."""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted

from nhanes_ai.schema import FAMILY_FIELDS, FEATURES, NUMERIC


def derive_features(frame):
    """One shared definition for training, UI and inference."""
    result = frame.copy()
    result["bmi"] = result.weight_kg / (result.height_cm / 100).pow(2)
    result["fat_mass_kg"] = result.weight_kg * result.body_fat_pct / 100
    result["fat_free_mass_kg"] = result.weight_kg - result.fat_mass_kg
    return result[FEATURES]


class FeatureEncoder(TransformerMixin, BaseEstimator):
    """Stable family-history encoding with an explicit unknown category.

    ID, survey cycle, disease questions and lab measurements are never features.
    Fixed categories avoid train/inference column drift even if a training subset lacks
    a category. Refused/don't-know family history never becomes a negative answer.
    """

    @staticmethod
    def encode(frame):
        missing = set(FEATURES) - set(frame.columns)
        if missing:
            raise ValueError(f"Missing model inputs: {sorted(missing)}")
        numeric = (
            frame[NUMERIC].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
        )
        encoded = [numeric]
        for name in FAMILY_FIELDS:
            codes = frame[name].map({0: "no", 1: "yes"}).fillna("unknown")
            categorical = pd.Series(
                pd.Categorical(codes, categories=["no", "yes", "unknown"]),
                index=frame.index,
                name=name,
            )
            encoded.append(pd.get_dummies(categorical, prefix=name, dtype=float))
        return pd.concat(encoded, axis=1)

    def fit(self, X, y=None):
        self.columns_ = self.encode(X).columns.to_numpy()
        self.n_features_in_ = len(FEATURES)
        self.feature_names_in_ = np.array(FEATURES, dtype=object)
        return self

    def transform(self, X):
        check_is_fitted(self, "columns_")
        return self.encode(X).reindex(columns=self.columns_).to_numpy(dtype=float)

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self, "columns_")
        return self.columns_


def preprocessing():
    """All learned medians and scaling statistics are fitted on training rows only."""
    return Pipeline(
        [
            ("encode", FeatureEncoder()),
            ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scale", StandardScaler()),
        ]
    )
