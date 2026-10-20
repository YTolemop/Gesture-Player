"""Independent temporal histories and exclusive joint output; no student answers."""
import threading
import time
from core.features import validate_prediction
from core.types import Prediction
from network.commands import Commands, CHANNELS
from student.filtering import StudentFilter

class OutputRouter:
    def __init__(self):
        self.lock = threading.RLock()
        self.filters = {channel: StudentFilter() for channel in CHANNELS}
        self.output = Commands()
        self.generated = float('-inf')
        self.error = ''

    def clear(self, enabled=False):
        with self.lock:
            self.output = Commands()
            self.generated = time.monotonic()
            if enabled:
                for temporal_filter in self.filters.values():
                    temporal_filter.reset()

    def update(self, predictions=None, tracked=True, enabled=False):
        with self.lock:
            now = time.monotonic()
            predictions = predictions or {}
            outputs = dict.fromkeys(CHANNELS, 'NONE')
            try:
                labels = {channel: validate_prediction(predictions.get(channel, Prediction()))
                          for channel in CHANNELS} if tracked else dict.fromkeys(CHANNELS, 'NONE')
                joint = labels['both'] != 'NONE'
                for channel in CHANNELS:
                    accepted = labels[channel] != 'NONE' and (channel == 'both' if joint else channel != 'both')
                    if not accepted:
                        if enabled:
                            self.filters[channel].reset()
                        continue
                    label = self.filters[channel].update(predictions[channel], now) if enabled else labels[channel]
                    if label not in ('NONE', labels[channel]):
                        # A legitimate filter may briefly bridge a previous label.
                        validate_prediction(Prediction(label, True, 0, 1))
                    outputs[channel] = label
                self.output = Commands(**outputs)
                self.error = ''
            except Exception as exc:
                self.output = Commands()
                self.error = str(exc)
            self.generated = now
            return self.output

    def read_commands(self):
        with self.lock:
            return self.output if time.monotonic() - self.generated <= .5 else Commands()

    def read(self):
        return ' / '.join(f'{key}={value}' for key, value in self.read_commands().payload().items())
