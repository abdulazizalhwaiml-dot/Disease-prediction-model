"""Serializable preprocessing shared verbatim by training, inference and SHAP."""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted

from nhanes_ai.schema import ETHNICITY, FEATURES, NUMERIC


class FeatureEncoder(TransformerMixin, BaseEstimator):
    """Stable pd.get_dummies encoding with an explicit unknown category.

    ID, survey cycle, disease questions and lab measurements are never features.
    Fixed categories avoid train/inference column drift even if a training subset lacks
    a category. Unknown values are encoded explicitly, never mapped to an ethnic group.
    """

    @staticmethod
    def encode(frame):
        missing = set(FEATURES) - set(frame.columns)
        if missing:
            raise ValueError(f"Missing model inputs: {sorted(missing)}")
        numeric = (
            frame[NUMERIC].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
        )
        codes = frame.ethnicity.map({code: str(code) for code in ETHNICITY}).fillna("unknown")
        ethnicity = pd.Series(
            pd.Categorical(codes, categories=[*map(str, ETHNICITY), "unknown"]),
            index=frame.index,
            name="ethnicity",
        )
        dummies = pd.get_dummies(ethnicity, prefix="ethnicity", dtype=float)
        return pd.concat([numeric, dummies], axis=1)

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
