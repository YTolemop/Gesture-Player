from core.types import Prediction


class StudentFilter:
    def update(self, prediction: Prediction, timestamp: float) -> str:
        """Optional: read prediction.label and prediction.valid.
        timestamp is local monotonic time in seconds. Store history on self.
        Return a label string or NONE; do not retain unknown or stale attacks.
        See README for initialization, state storage, and return contracts.
        """
        raise NotImplementedError('Implement StudentFilter.update; see README')

    def reset(self) -> None:
        """Optional: clear all history used by update and return None.
        See README for details.
        """
        raise NotImplementedError('Implement StudentFilter.reset; see README')
