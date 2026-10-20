"""Three KNN banks using the learner's same normalizer and KNN interfaces."""
from dataclasses import replace
from pathlib import Path
import json
import numpy as np
from core.dataset import read_batch
from core.features import feature, validate_prediction
from core.labels import LABELS
from core.model_io import validate_training, CheckedModel
from core.types import Prediction
from network.commands import Commands, CHANNELS
from student.knn import StudentKNN

FORMAT = 'gui-three-channel-v1'

def channel_sample(sample, channel):
    if channel == 'left':
        return replace(sample, right=None)
    if channel == 'right':
        return replace(sample, left=None)
    if channel == 'both':
        return sample if sample.left is not None and sample.right is not None else replace(sample, left=None, right=None)
    raise ValueError('通道必須為 left、right 或 both')

def vector(sample, channel, config):
    return feature(channel_sample(sample, channel), config)

def settings(config):
    return {key: value for key, value in config.items() if key != 'filter_enabled'}

def recordings(paths, purpose):
    for path in paths:
        samples, labels, meta = read_batch(path)
        if meta['purpose'] != purpose:
            continue
        channel = meta.get('channel')
        if channel not in CHANNELS:
            raise ValueError(f'{Path(path).name} 是未標通道的舊批次；請使用新版 UI 重新錄製並另存，原檔不會被修改')
        for sample, label in zip(samples, labels):
            yield sample, int(label), channel

def train(paths, path, config):
    banks = {channel: ([], []) for channel in CHANNELS}
    rejected = dict.fromkeys(CHANNELS, 0)
    for sample, label, channel in recordings(paths, 'train'):
        result = vector(sample, channel, config)
        if result.valid:
            banks[channel][0].append(result.features)
            banks[channel][1].append(label)
        else:
            rejected[channel] += 1
    payload, dimensions, counts = {}, set(), {}
    for channel, (features, labels) in banks.items():
        if not features:
            raise ValueError(f'{channel} 通道沒有可用訓練資料；請檢查錄製通道、入鏡的手和正規化實作')
        x, y = np.asarray(features, np.float32), np.asarray(labels, np.int64)
        validate_training(x, y, config)
        model = StudentKNN()
        model.fit(x, y, config)
        dimensions.add(x.shape[1])
        payload[channel + '_features'], payload[channel + '_labels'] = x, y
        counts[channel] = len(y)
    if len(dimensions) != 1:
        raise ValueError('三個通道必須使用相同的固定特徵維度，請使用 README 的 131 維範例')
    payload['metadata'] = np.asarray(json.dumps({'format': FORMAT, 'config': settings(config), 'labels': LABELS}))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as stream:
        np.savez_compressed(stream, **payload)
    return {'training_samples': sum(counts.values()), 'channel_samples': counts,
            'normalization_rejected': sum(rejected.values()), 'rejected_by_channel': rejected}

class ChannelModel:
    def __init__(self, models, config):
        self.models, self.config = models, config

    def predict_channels(self, sample):
        predictions = {}
        for channel in CHANNELS:
            result = vector(sample, channel, self.config)
            predictions[channel] = self.models[channel].predict(result.features) if result.valid else Prediction()
            validate_prediction(predictions[channel])
        return predictions

def load_model(path, config):
    models, dimensions = {}, set()
    with np.load(path, allow_pickle=False) as data:
        if 'metadata' not in data:
            raise ValueError('這是舊版單通道模型；新版請使用三通道錄製資料重新訓練 models/model.npz')
        meta = json.loads(str(data['metadata']))
        if meta != {'format': FORMAT, 'config': settings(config), 'labels': LABELS}:
            raise ValueError('模型版本或設定不相容，請以新版三通道資料重新訓練')
        for channel in CHANNELS:
            x, y = data[channel + '_features'], data[channel + '_labels']
            validate_training(x, y, config)
            model = StudentKNN()
            model.fit(x, y, config)
            dimensions.add(x.shape[1])
            models[channel] = CheckedModel(model, x.shape[1])
    if len(dimensions) != 1:
        raise ValueError('模型的三個通道特徵維度不一致')
    return ChannelModel(models, config)

def evaluate(paths, path, config):
    model = load_model(path, config)
    matrices = {channel: np.zeros((11, 11), dtype=int) for channel in CHANNELS}
    rejected = 0
    for sample, label, channel in recordings(paths, 'test'):
        predictions = model.predict_channels(sample)
        values = {key: validate_prediction(value) for key, value in predictions.items()}
        commands = Commands(both=values['both']) if values['both'] != 'NONE' else Commands(left=values['left'], right=values['right'])
        actual = commands.both if channel != 'both' and commands.both != 'NONE' else getattr(commands, channel)
        matrices[channel][label, LABELS.index(actual)] += 1
        rejected += not vector(sample, channel, config).valid
    total = sum(int(matrix.sum()) for matrix in matrices.values())
    if not total:
        raise ValueError('沒有獨立 test 批次；請切換用途為 test 後另外錄製，不能用 train 充當測試')
    return {'independent_test': True, 'samples': total, 'normalization_rejected': rejected,
            'labels': LABELS, 'channels': {channel: {'samples': int(matrix.sum()),
                'accuracy': float(np.trace(matrix) / matrix.sum()) if matrix.sum() else None,
                'confusion_matrix': matrix.tolist()} for channel, matrix in matrices.items()}}
