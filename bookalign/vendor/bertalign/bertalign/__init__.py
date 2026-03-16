"""
Bertalign initialization
"""

__author__ = "Jason (bfsujason@163.com)"
__version__ = "1.1.0"

model_name = "sentence-transformers/LaBSE"
model = None


def configure_model(name=None):
    global model_name, model
    if name and name != model_name:
        model_name = name
        model = None


def get_model():
    global model
    if model is None:
        from bertalign.encoder import Encoder

        model = Encoder(model_name)
    return model

from bertalign.aligner import Bertalign
