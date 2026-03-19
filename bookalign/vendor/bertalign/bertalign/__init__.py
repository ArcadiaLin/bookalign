"""
Bertalign initialization
"""

__author__ = "Jason (bfsujason@163.com)"
__version__ = "1.1.0"

model_name = "sentence-transformers/LaBSE"
model_device = "cuda"
model = None


def configure_model(name=None, device=None):
    global model_name, model_device, model
    if name and name != model_name:
        model_name = name
        model = None
    if device and device != model_device:
        model_device = device
        model = None


def get_model():
    global model
    if model is None:
        from bertalign.encoder import Encoder

        model = Encoder(model_name, device=model_device)
    return model

from bertalign.aligner import Bertalign
