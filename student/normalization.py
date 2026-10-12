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
        See README for the basic right-hand and optional mixed-hand examples.
        """
        raise NotImplementedError('Implement StudentNormalizer.transform; see README')
