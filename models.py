# models.py

import streamlit as st
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import DepthwiseConv2D as KDepthwise
from config import (
    AGE_MODEL_PATH,
    VAR_MODEL_PATH,
    LABEL_MODEL_PATH,
    AGE_MIN,
    AGE_MAX,
    # VARIETIES,
    # DISEASES
)

# 1) Patch DepthwiseConv2D to drop the unsupported 'groups' arg
class DepthwiseConv2D(KDepthwise):
    def __init__(self, *args, **kwargs):
        kwargs.pop("groups", None)
        super().__init__(*args, **kwargs)

@st.cache_resource
def load_models():
    custom = {"DepthwiseConv2D": DepthwiseConv2D}

    # 2) Pass compile=False to skip deserializing loss/metrics (mse, etc.)
    age_m   = load_model(str(AGE_MODEL_PATH), custom_objects=custom, compile=False)
    var_m   = load_model(str(VAR_MODEL_PATH), custom_objects=custom, compile=False)
    lbl_m   = load_model(str(LABEL_MODEL_PATH), custom_objects=custom, compile=False)
    return age_m, var_m, lbl_m

def preprocess_image(img: Image.Image, target_size=(224, 224)) -> np.ndarray:
    """
    Resize, optionally rotate, and normalize a PIL image.
    - If input is 640x480, rotate to 480x640
    - Resize to (224, 224)
    - Normalize pixel values to [0, 1]
    - Convert to batch shape (1, H, W, C)
    """
    # Rotate if size is (640, 480), to match training-time augmentation
    if img.size == (640, 480):
        img = img.rotate(90, expand=True)

    # Resize to input shape
    img = img.resize(target_size)

    # Convert to array and normalize
    arr = np.array(img).astype("float32") / 255.0

    # Handle grayscale images by replicating channels
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)

    # Add batch dimension
    return np.expand_dims(arr, axis=0)

def predict_all(img: Image.Image):
    """
    Run inference through all three models:
    1) Age prediction (denormalized)
    2) Variety classification
    3) Disease classification
    Returns:
        age_days (float), variety (str), label (str)
    """
    # Load models
    age_m, var_m, lbl_m = load_models()

    # Preprocess image
    x = preprocess_image(img)

    # Predict normalized age, then denormalize to actual age
    age_norm = age_m.predict(x, verbose=0)[0][0]
    age_days = age_norm * (AGE_MAX - AGE_MIN) + AGE_MIN

    # Predict variety class
    var_probs = var_m.predict(x, verbose=0)[0]
    var_idx = int(np.argmax(var_probs))
    VARIETIES = ['ADT45', 'IR20', 'KarnatakaPonni', 'Onthanel', 'Ponni', 'Surya', 'Zonal', 'AndraPonni', 'AtchayaPonni', 'RR']


    variety = VARIETIES[var_idx]

    # Predict disease label
    lbl_probs = lbl_m.predict(x, verbose=0)[0]
    lbl_idx = int(np.argmax(lbl_probs))
    DISEASES = ['bacterial_leaf_blight', 'bacterial_leaf_streak', 'bacterial_panicle_blight', 'blast', 'brown_spot', 'dead_heart', 'downy_mildew', 'hispa', 'normal', 'tungro']


    label = DISEASES[lbl_idx]

    return float(age_days), variety, label