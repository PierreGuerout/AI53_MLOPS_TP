import logging
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from PIL import Image
from pydantic import BaseModel, Field

from app.model import LeafModel, load_model, predict

LOGGER = logging.getLogger(__name__)
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 8_000_000


class Prediction(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    model_version: str


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.model = None
    try:
        application.state.model = load_model()
    except Exception:
        LOGGER.exception("Could not load the model artifact")
    yield
    application.state.model = None


app = FastAPI(title="Bean Leaf Classifier", lifespan=lifespan)


@app.get("/", include_in_schema=False)
def prediction_page() -> FileResponse:
    return FileResponse(Path(__file__).with_name("index.html"), media_type="text/html")


def ready_model(request: Request) -> LeafModel:
    model = request.app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not ready.")
    return model


def decode_image(file: UploadFile) -> Image.Image:
    image_bytes = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Use an image of 5 MiB or less.")

    try:
        with Image.open(BytesIO(image_bytes), formats=("JPEG", "PNG")) as image:
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=413, detail="Use an image of 8 million pixels or less."
                )
            return image.convert("RGB")
    except Image.DecompressionBombError as error:
        raise HTTPException(status_code=413, detail="Image dimensions are too large.") from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=415, detail="Upload a valid JPEG or PNG image.") from error


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(request: Request) -> dict[str, str]:
    model = ready_model(request)
    return {"status": "ready", "model_version": model.version}


@app.post("/predict", response_model=Prediction)
def classify(request: Request, file: Annotated[UploadFile, File()]) -> Prediction:
    model = ready_model(request)
    image = decode_image(file)

    label, confidence = predict(model, image)
    return Prediction(
        label=label,
        confidence=confidence,
        model_version=model.version,
    )
