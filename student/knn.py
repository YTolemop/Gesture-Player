import numpy as np
from core.labels import LABELS
from core.types import Prediction


class StudentKNN:
    def fit(self, features, labels, config: dict) -> None:
        """Required: features is float32 (N, 63); labels is integer (N,), 0..9.
        Store training data and settings on self for predict; do not read files.
        Return None. See README for input contracts and useful operations.
        """
        raise NotImplementedError('Implement StudentKNN.fit; see README')

    def predict(self, features) -> Prediction:
        """Required: features is one float32 vector of shape (63,).
        Classify using the data stored by fit. Choose a distance metric,
        neighbors, voting, deterministic ties, and unknown rejection rules.
        Return Prediction; use LABELS[class_id] to obtain a label string.
        See README for the return contract.
        """
        raise NotImplementedError('Implement StudentKNN.predict; see README')
