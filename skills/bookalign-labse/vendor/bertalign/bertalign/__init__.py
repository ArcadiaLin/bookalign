"""
Bertalign initialization
"""

__author__ = "Jason (bfsujason@163.com)"
__version__ = "1.1.0"

model_name = "sentence-transformers/LaBSE"
model_device = "cuda"
model_backend = "local"
model_api_url = None
model_api_token = None
model_api_token_env = "HF_TOKEN"
model_request_timeout = 60.0
model = None


def configure_model(
    name=None,
    device=None,
    *,
    backend=None,
    api_url=None,
    api_token=None,
    api_token_env=None,
    request_timeout=None,
):
    global model_name, model_device, model_backend, model_api_url, model_api_token, model_api_token_env, model_request_timeout, model
    if name and name != model_name:
        model_name = name
        model = None
    if device and device != model_device:
        model_device = device
        model = None
    if backend and backend != model_backend:
        model_backend = backend
        model = None
    if api_url != model_api_url:
        model_api_url = api_url
        model = None
    if api_token != model_api_token:
        model_api_token = api_token
        model = None
    if api_token_env and api_token_env != model_api_token_env:
        model_api_token_env = api_token_env
        model = None
    if request_timeout is not None and request_timeout != model_request_timeout:
        model_request_timeout = request_timeout
        model = None


def get_model():
    global model
    if model is None:
        from bertalign.encoder import Encoder

        model = Encoder(
            model_name,
            device=model_device,
            backend=model_backend,
            api_url=model_api_url,
            api_token=model_api_token,
            api_token_env=model_api_token_env,
            request_timeout=model_request_timeout,
        )
    return model

from bertalign.aligner import Bertalign
