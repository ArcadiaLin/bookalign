import json
import numpy as np
import os
import torch
from urllib import request

from bertalign.utils import yield_overlaps


class Encoder:
    def __init__(
        self,
        model_name,
        device=None,
        *,
        backend='local',
        api_url=None,
        api_token=None,
        api_token_env='HF_TOKEN',
        request_timeout=60.0,
    ):
        requested_device = (device or 'auto').strip().lower()
        if requested_device == 'auto':
            requested_device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if backend == 'local' and requested_device.startswith('cuda') and not torch.cuda.is_available():
            raise RuntimeError('CUDA device was requested for Bertalign, but torch.cuda.is_available() is False.')
        self.device = requested_device
        self.model_name = model_name
        self.backend = backend
        self.api_url = api_url
        self.api_token = api_token
        self.api_token_env = api_token_env
        self.request_timeout = request_timeout
        self.model = None
        if self.backend == 'local':
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name, device=self.device)
        elif self.backend == 'hf_inference':
            self.api_url = self.api_url or (
                f'https://router.huggingface.co/hf-inference/models/{model_name}/pipeline/feature-extraction'
            )
        else:
            raise ValueError(f'Unsupported encoder backend: {self.backend}')

    def transform(self, sents, num_overlaps):
        overlaps = []
        for line in yield_overlaps(sents, num_overlaps):
            overlaps.append(line)

        sent_vecs = self._encode_overlaps(overlaps)
        embedding_dim = sent_vecs.size // (len(sents) * num_overlaps)
        sent_vecs.resize(num_overlaps, len(sents), embedding_dim)

        len_vecs = [len(line.encode("utf-8")) for line in overlaps]
        len_vecs = np.array(len_vecs)
        len_vecs.resize(num_overlaps, len(sents))

        return sent_vecs, len_vecs

    def _encode_overlaps(self, overlaps):
        if self.backend == 'local':
            return self.model.encode(
                overlaps,
                batch_size=8,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True,
            )
        response = self._post_json({'inputs': overlaps})
        return self._coerce_embedding_matrix(response, expected_rows=len(overlaps))

    def _post_json(self, payload):
        token = self.api_token or os.environ.get(self.api_token_env or 'HF_TOKEN')
        if not token:
            raise RuntimeError(
                f'Hugging Face token is required for backend={self.backend}. '
                f'Set {self.api_token_env or "HF_TOKEN"} or pass hf_api_token explicitly.'
            )
        data = json.dumps(payload).encode('utf-8')
        req = request.Request(
            self.api_url,
            data=data,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        with request.urlopen(req, timeout=self.request_timeout) as response:
            return json.loads(response.read().decode('utf-8'))

    def _coerce_embedding_matrix(self, payload, *, expected_rows):
        if isinstance(payload, dict):
            error = payload.get('error') or payload.get('message') or payload
            raise RuntimeError(f'Hugging Face inference request failed: {error}')
        if expected_rows == 1 and _is_number_list(payload):
            rows = [payload]
        else:
            rows = payload
        if not isinstance(rows, list) or len(rows) != expected_rows:
            raise RuntimeError(
                f'Unexpected embedding payload shape from Hugging Face API: expected {expected_rows} rows, got {type(payload).__name__}'
            )
        matrix = np.vstack([_normalize_vector(_coerce_embedding_row(item)) for item in rows])
        return matrix


def _coerce_embedding_row(item):
    if _is_number_list(item):
        return np.asarray(item, dtype=np.float32)
    array = np.asarray(item, dtype=np.float32)
    if array.ndim == 0:
        raise RuntimeError('Embedding row is scalar; expected vector or token matrix.')
    if array.ndim == 1:
        return array
    last_dim = array.shape[-1]
    return array.reshape(-1, last_dim).mean(axis=0)


def _normalize_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def _is_number_list(value):
    return isinstance(value, list) and all(isinstance(item, (int, float)) for item in value)
