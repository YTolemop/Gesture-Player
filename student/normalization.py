import numpy as np
from core.types import RawHandSample, FeatureResult


class StudentNormalizer:
    def transform(self, sample: RawHandSample, config: dict) -> FeatureResult:
        """Required: sample.left/right are (21, 3) arrays or None; at least one exists.
        sample.width and sample.height are the image dimensions in pixels.
        Convert to a common pixel scale, center on the wrist, normalize by
        palm size, and return a nonempty float32 vector of shape (D,).
        Keep D and slot ordering consistent for all accepted samples, including
        mixed single/dual hands. Return invalid with features=None to reject
        samples your algorithm does not support. Preserve orientation as needed.
        Return FeatureResult with featureVersion=config['feature_version'].
        The current GUI trains separate left/right/both banks. Support each
        handedness combination with the same fixed dimension (README: 131).
        Left/right calls contain only that side; the joint bank requires both.
        See README for the complete three-channel reference implementation.
        """
        raise NotImplementedError('Implement StudentNormalizer.transform; see README')
