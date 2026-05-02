from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

COPY_ROOT = Path(__file__).resolve().parents[1]
if str(COPY_ROOT) not in sys.path:
    sys.path.insert(0, str(COPY_ROOT))

from align.bertalign_adapter import _ensure_vendor_path  # noqa: E402

_ensure_vendor_path()

from bertalign.encoder import Encoder  # noqa: E402


def test_hf_inference_backend_normalizes_and_reshapes_embeddings(monkeypatch: pytest.MonkeyPatch):
    captured = {}

    def fake_post_json(self, payload):
        captured["payload"] = payload
        return [
            [3.0, 4.0],
            [5.0, 12.0],
            [8.0, 15.0],
            [7.0, 24.0],
        ]

    monkeypatch.setattr(Encoder, "_post_json", fake_post_json)

    encoder = Encoder(
        "rasa/LaBSE",
        backend="hf_inference",
        api_url="https://router.huggingface.co/hf-inference/models/rasa/LaBSE/pipeline/feature-extraction",
        api_token="test-token",
    )
    sent_vecs, len_vecs = encoder.transform(["alpha", "beta"], 2)

    assert captured["payload"]["inputs"] == ["alpha", "beta", "PAD", "alpha beta"]
    assert sent_vecs.shape == (2, 2, 2)
    assert len_vecs.shape == (2, 2)
    assert np.allclose(sent_vecs[0, 0], np.array([0.6, 0.8], dtype=np.float32))
    assert np.allclose(np.linalg.norm(sent_vecs.reshape(-1, 2), axis=1), 1.0)
