"""Load the versioned Phase 1 artifact and score one leaf image."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image


MODEL_PATH = Path(__file__).resolve().parents[1] / "model" / "bean-cnn.onnx"
LABELS = ("angular_leaf_spot", "bean_rust", "healthy")
IMAGE_SIZE = 96


@dataclass(frozen=True)
class LeafModel:
    session: ort.InferenceSession
    version: str


def load_model(path: Path = MODEL_PATH) -> LeafModel:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    session = ort.InferenceSession(
        str(path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    metadata = session.get_modelmeta().custom_metadata_map
    version = metadata.get("model_version")
    if not version or metadata.get("class_names") != ",".join(LABELS):
        raise ValueError("Model version or label metadata is missing or invalid")
    return LeafModel(session=session, version=version)


def preprocess(image: Image.Image) -> np.ndarray:
    # Match the prepared Phase 1 inputs, including the JPEG encoding step.
    resized = image.convert("RGB").resize(
        (IMAGE_SIZE, IMAGE_SIZE), Image.Resampling.BILINEAR
    )
    with BytesIO() as encoded:
        resized.save(encoded, format="JPEG", quality=92)
        encoded.seek(0)
        with Image.open(encoded) as prepared:
            pixels = np.asarray(prepared, dtype=np.float32) / 255.0

    normalized = (pixels - 0.5) / 0.5
    return normalized.transpose(2, 0, 1)[None, ...]


def predict(model: LeafModel, image: Image.Image) -> tuple[str, float]:
    (logits,) = model.session.run(["logits"], {"pixels": preprocess(image)})
    scores = logits[0]
    weights = np.exp(scores - scores.max())
    probabilities = weights / weights.sum()
    index = int(probabilities.argmax())
    return LABELS[index], float(probabilities[index])
