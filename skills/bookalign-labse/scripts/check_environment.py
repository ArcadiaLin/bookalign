"""Inspect Bookalign runtime availability without mutating project state."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
from pathlib import Path
import sys

from _bootstrap import ensure_skill_root


_LOCAL_MODEL_CANDIDATES = [
    Path("/root/models/LaBSE"),
    Path("/root/.cache/huggingface/hub/models--sentence-transformers--LaBSE"),
]


def _module_status(name: str) -> dict[str, object]:
    spec = importlib.util.find_spec(name)
    return {
        "name": name,
        "available": spec is not None,
        "origin": None if spec is None else spec.origin,
    }


def _torch_status() -> dict[str, object]:
    status = _module_status("torch")
    if not status["available"]:
        status["cuda_built"] = False
        status["cuda_available"] = False
        status["device_count"] = 0
        return status

    try:
        import torch
    except Exception as exc:  # pragma: no cover - defensive reporting
        status["available"] = False
        status["error"] = repr(exc)
        status["cuda_built"] = False
        status["cuda_available"] = False
        status["device_count"] = 0
        return status

    status["cuda_built"] = bool(torch.backends.cuda.is_built())
    status["cuda_version"] = torch.version.cuda
    status["cuda_available"] = bool(torch.cuda.is_available())
    status["device_count"] = int(torch.cuda.device_count()) if status["cuda_available"] else 0
    status["cuda_devices"] = [
        torch.cuda.get_device_name(index)
        for index in range(status["device_count"])
    ]
    return status


def _model_candidate_status(path: Path) -> dict[str, object]:
    config_path = path / "config.json"
    modules_path = path / "modules.json"
    sentence_transformers_ready = path.is_dir() and config_path.exists() and modules_path.exists()
    return {
        "path": str(path),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "sentence_transformers_ready": sentence_transformers_ready,
    }


def inspect_environment() -> dict[str, object]:
    skill_root = ensure_skill_root()
    vendor_root = skill_root / "vendor" / "bertalign"

    core_modules = [
        "ebooklib",
        "lxml",
        "pysbd",
    ]
    optional_align_modules = [
        "numpy",
        "faiss",
        "numba",
        "googletrans",
        "sentence_transformers",
        "sentence_splitter",
    ]

    torch_status = _torch_status()
    hf_token_present = bool(os.environ.get("HF_TOKEN"))
    model_candidates = [_model_candidate_status(path) for path in _LOCAL_MODEL_CANDIDATES]
    local_model_ready = any(candidate["sentence_transformers_ready"] for candidate in model_candidates)
    preferred_local_model = next(
        (candidate["path"] for candidate in model_candidates if candidate["sentence_transformers_ready"]),
        None,
    )

    local_align_dependencies_ready = all(_module_status(name)["available"] for name in optional_align_modules)
    if not torch_status["available"]:
        local_align_dependencies_ready = False

    if local_align_dependencies_ready and local_model_ready and torch_status["cuda_available"]:
        recommended_backend = "local_cuda"
        recommended_model_name = preferred_local_model
        recommended_device = "cuda"
    elif local_align_dependencies_ready and local_model_ready:
        recommended_backend = "local_cpu"
        recommended_model_name = preferred_local_model
        recommended_device = "cpu"
    elif hf_token_present:
        recommended_backend = "hf_inference"
        recommended_model_name = "rasa/LaBSE"
        recommended_device = "cpu"
    elif local_align_dependencies_ready:
        recommended_backend = "local_model_missing"
        recommended_model_name = None
        recommended_device = "cuda" if torch_status["cuda_available"] else "cpu"
    else:
        recommended_backend = "inspection_only"
        recommended_model_name = None
        recommended_device = None

    return {
        "skill_root": str(skill_root),
        "python": {
            "executable": sys.executable,
            "version": platform.python_version(),
        },
        "vendor": {
            "bertalign_root": str(vendor_root),
            "exists": vendor_root.exists(),
        },
        "core_modules": [_module_status(name) for name in core_modules],
        "optional_align_modules": [_module_status(name) for name in optional_align_modules],
        "local_align_dependencies_ready": local_align_dependencies_ready,
        "local_model_candidates": model_candidates,
        "local_model_ready": local_model_ready,
        "preferred_local_model": preferred_local_model,
        "torch": torch_status,
        "hf_token_present": hf_token_present,
        "recommended_backend": recommended_backend,
        "recommended_model_name": recommended_model_name,
        "recommended_device": recommended_device,
        "proxy_env": {
            key: os.environ.get(key)
            for key in ("HF_ENDPOINT", "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy")
            if os.environ.get(key)
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Bookalign runtime availability.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON only.",
    )
    args = parser.parse_args()

    report = inspect_environment()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["recommended_backend"] == "inspection_only":
        print(
            "Recommendation: inspection APIs are available, but no alignment backend is fully ready. "
            "Configure HF_TOKEN or install local alignment dependencies before running Bertalign."
        )
    elif report["recommended_backend"] == "local_model_missing":
        print(
            "Recommendation: local alignment dependencies exist, but no ready local SentenceTransformer model "
            "path was found. Prefer an explicit local model path or switch to hf_inference."
        )


if __name__ == "__main__":
    main()
