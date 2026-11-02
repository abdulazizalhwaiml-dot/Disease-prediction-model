"""Use XGBoost's portable model format instead of platform-specific memory snapshots."""

from sklearn.frozen import FrozenEstimator
from xgboost import Booster, XGBClassifier


class PortableBooster(Booster):
    """Joblib-compatible wrapper whose payload is the official UBJSON model format.

    XGBoost's ordinary pickle captures an internal memory snapshot. A model exported
    with save_raw(raw_format='ubj') can instead be loaded by the native Windows/Linux
    libraries without changing trees, calibration or prediction thresholds.
    """

    def __getstate__(self):
        return {
            "model_ubj": bytes(self.save_raw(raw_format="ubj")),
            "config_json": self.save_config(),
        }

    def __setstate__(self, state):
        Booster.__init__(self, model_file=bytearray(state["model_ubj"]))
        self.load_config(state["config_json"])


def make_portable(pipeline):
    """Replace only the serialized booster representation; never fit or recalibrate."""
    for calibrated in pipeline.named_steps["classifier"].calibrated_classifiers_:
        estimator = calibrated.estimator
        if isinstance(estimator, FrozenEstimator):
            estimator = estimator.estimator
        if isinstance(estimator, XGBClassifier) and not isinstance(
            estimator.get_booster(), PortableBooster
        ):
            original = estimator.get_booster()
            portable = PortableBooster(model_file=bytearray(original.save_raw(raw_format="ubj")))
            portable.load_config(original.save_config())
            estimator._Booster = portable
    return pipeline
