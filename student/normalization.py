import numpy as np
from core.types import RawHandSample, FeatureResult


class StudentNormalizer:
    def transform(self, sample: RawHandSample, config: dict) -> FeatureResult:
        """Required: sample.right is a valid right-hand array of shape (21, 3).
        sample.width and sample.height are the image dimensions in pixels.
        Convert to a common pixel scale, center on the wrist, normalize by
        palm size, and flatten to 63 float32 values. Preserve orientation.
        Return FeatureResult with featureVersion=config['feature_version'].
        See README for data access, NumPy operations, and return contracts.
        """
        raise NotImplementedError('Implement StudentNormalizer.transform; see README')
