import numpy as np
import torch

from sentence_transformers import SentenceTransformer
from bertalign.utils import yield_overlaps

class Encoder:
    def __init__(self, model_name, device=None):
        requested_device = (device or 'auto').strip().lower()
        if requested_device == 'auto':
            requested_device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if requested_device.startswith('cuda') and not torch.cuda.is_available():
            raise RuntimeError('CUDA device was requested for Bertalign, but torch.cuda.is_available() is False.')
        self.device = requested_device
        self.model = SentenceTransformer(model_name, device=self.device)
        self.model_name = model_name

    def transform(self, sents, num_overlaps):
        overlaps = []
        for line in yield_overlaps(sents, num_overlaps):
            overlaps.append(line)

        sent_vecs = self.model.encode(
            overlaps,
            batch_size=8,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        embedding_dim = sent_vecs.size // (len(sents) * num_overlaps)
        sent_vecs.resize(num_overlaps, len(sents), embedding_dim)

        len_vecs = [len(line.encode("utf-8")) for line in overlaps]
        len_vecs = np.array(len_vecs)
        len_vecs.resize(num_overlaps, len(sents))

        return sent_vecs, len_vecs
