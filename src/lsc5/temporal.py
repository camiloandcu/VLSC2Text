"""Masked opaque TCN; native lengths and real zero frames are preserved."""
import numpy as np
import torch
from torch import nn

HYPERPARAMETERS = {'input_dim': 1662, 'width': 64, 'kernel': 5, 'dilations': [1, 2, 4],
                  'dropout': .2, 'optimizer': 'AdamW', 'lr': .001, 'weight_decay': .001,
                  'grad_clip': 1, 'loss': 'cross_entropy', 'batch_per_signer_class': 4,
                  'warmup_epochs': 5, 'scheduler': 'cosine', 'end_lr_fraction': .01,
                  'scaler_weighting': 'real_frames_population'}


def collate(sequences):
    if not sequences or any(x.ndim != 2 or x.shape[1] != 1662 or not len(x) for x in sequences):
        raise ValueError('Expected nonempty native sequences')
    n = max(map(len, sequences))
    x = torch.zeros(len(sequences), n, 1662)
    mask = torch.zeros(len(sequences), n, dtype=torch.bool)
    for i, value in enumerate(sequences):
        x[i, :len(value)] = torch.as_tensor(value)
        mask[i, :len(value)] = True
    return x, mask


class OpaqueTCN(nn.Module):
    def __init__(self):
        super().__init__()
        self.projection = nn.Linear(1662, 64)
        self.convs = nn.ModuleList([nn.Conv1d(64, 64, 5, padding=2*d, dilation=d) for d in [1, 2, 4]])
        self.norms = nn.ModuleList([nn.LayerNorm(64) for _ in range(3)])
        self.activation = nn.GELU()
        self.dropout = nn.Dropout(.2)
        self.head = nn.Linear(64, 5)

    def forward(self, x, mask):
        if (x.ndim != 3 or x.shape[-1] != 1662 or mask.shape != x.shape[:2]
                or mask.dtype != torch.bool or torch.any(mask.sum(1) == 0)):
            raise ValueError('Invalid temporal batch/mask')
        valid = mask.unsqueeze(-1)
        h = self.projection(x)*valid
        for conv, norm in zip(self.convs, self.norms):
            branch = conv(h.transpose(1, 2)).transpose(1, 2)
            h = (h+self.dropout(self.activation(norm(branch))))*valid
        return self.head(h.sum(1)/mask.sum(1, keepdim=True))


def infer(model, sequences):
    model.eval()
    outputs = []
    with torch.inference_mode():
        for start in range(0, len(sequences), 16):
            outputs.append(model(*collate(sequences[start:start+16])))
        logits = torch.cat(outputs)
        return logits.numpy(), torch.softmax(logits, dim=1).numpy()
