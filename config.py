# config.py

# change DATABASE_URL, JWT_SECRET, and GEMINI_API_KEY

import os
from pathlib import Path

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
# Expect a full Postgres URI for Neon:
#   "postgresql://user:pass@branch.region.neon.tech/dbname"
DB_URL = "postgresql://paddy_db_owner:npg_4xERuCWalc6V@ep-gentle-fire-a1oyhbfb-pooler.ap-southeast-1.aws.neon.tech/paddy_db?sslmode=require"
if not DB_URL:
    raise RuntimeError("❌ DATABASE_URL not set. Export your Neon connection string.")

# -----------------------------------------------------------------------------
# JWT / Auth
# -----------------------------------------------------------------------------
# Secret key for signing JWTs (override via env)
JWT_SECRET               = "Shhhh"
JWT_ALGORITHM            = "HS256"
ACCESS_TOKEN_EXPIRE_MIN  = 60  # minutes

# -----------------------------------------------------------------------------
# Model paths
# -----------------------------------------------------------------------------
# Local paths in your repo where the .h5 files live
BASE_DIR                 = Path(__file__).parent
AGE_MODEL_PATH           = BASE_DIR / "models" / "age_model.h5"
VAR_MODEL_PATH           = BASE_DIR / "models" / "variety_model.h5"
LABEL_MODEL_PATH         = BASE_DIR / "models" / "label_model.h5"


# -----------------------------------------------------------------------------
# Max & Min age
# -----------------------------------------------------------------------------
# Max & Min age are used to correctly perform min-max scaling
AGE_MIN = 45.0
AGE_MAX = 82.0


# -----------------------------------------------------------------------------
# DISEASES & VARIETIES age
# -----------------------------------------------------------------------------
# To interprete the result from model correctly
DISEASES = ['bacterial_leaf_blight', 'bacterial_leaf_streak', 'bacterial_panicle_blight', 'blast', 'brown_spot', 'dead_heart', 'downy_mildew', 'hispa', 'normal', 'tungro']
VARIETIES = ['ADT45', 'IR20', 'KarnatakaPonni', 'Onthanel', 'Ponni', 'Surya', 'Zonal', 'AndraPonni', 'AtchayaPonni', 'RR']


# -----------------------------------------------------------------------------
# Gemini LLM API
# -----------------------------------------------------------------------------
# Your Gemini 2.0 "flash" API key (override via env)
GEMINI_API_KEY           = "AIzaSyCSqf83q824QAwTtH0lIismTFg_Cb0Gq50"
if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not set. Export your API key.")

# -----------------------------------------------------------------------------
# Prompt for AI feature
# -----------------------------------------------------------------------------
# Predefined prompt for interprete, seek advice, and add context.
# System prompt seeds every chat
SYSTEM_PROMPT = (
    "You are an expert rice agronomist advising smallholder farmers in {region}. "
    "Provide concise, straight-to-the-point answers in bullet points, "
    "focusing strictly on paddy rice plant farming techniques."
    "Do not ask user again any question."
    "On top of the response, do not say that you assume anything."
    "If you assume, then just answer it, and do not state in the response"
    "Limit all the response less than 300 words"
)

# Pre-defined "Interpret" prompt
INTERPRET_PROMPT = (
    "A rice plant is {age:.1f} days old, variety {variety}, "
    "and shows health status: {label}. Interpret what this means."
)

# Pre-defined "Get advice" prompt
ADVICE_PROMPT = (
    "A rice plant is {age:.1f} days old, variety {variety}, "
    "and has {label}. Provide practical, low-cost advice for prevention or treatment."
)


# -----------------------------------------------------------------------------
# PDF Reports
# -----------------------------------------------------------------------------
# Directory where generated PDFs will be stored before download
REPORTS_DIR              = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# -----------------------------------------------------------------------------
# Streamlit / App settings
# -----------------------------------------------------------------------------
# You can tweak Streamlit’s page config here, or other globals
PAGE_TITLE               = "Paddy Doctor"
PAGE_LAYOUT              = "centered"