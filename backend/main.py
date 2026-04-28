from fastapi import FastAPI, File, UploadFile
import numpy as np
import cv2
from PIL import Image
import pillow_heif
import io
from fastapi.middleware.cors import CORSMiddleware

from model import process_image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable HEIC support
pillow_heif.register_heif_opener()

@app.post("/scan")
async def scan_room(file: UploadFile = File(...)):
    contents = await file.read()

    # Load ANY format (HEIC, JPG, PNG)
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # Convert to OpenCV format
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    grid, spawns = process_image(img)

    return {
        "grid": grid,
        "spawns": spawns
    }