"""Only the approved opaque-feature pilot model is implemented here."""
import torch
from torch import nn


class RawStatsMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(3324, 128), nn.ReLU(), nn.Dropout(0.3),
                                    nn.Linear(128, 5))

    def forward(self, values):
        if values.ndim != 2 or values.shape[1] != 3324:
            raise ValueError("Expected opaque 3324-dimensional statistics")
        return self.layers(values)


def probabilities(model, values):
    model.eval()
    with torch.inference_mode():
        return torch.softmax(model(torch.as_tensor(values, dtype=torch.float32)), dim=1).numpy()
