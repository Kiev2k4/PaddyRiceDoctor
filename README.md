# PaddyRiceDoctor 🌾

**Crop Health & Variety Detection** — A collaborative AI-powered web application that helps smallholder farmers diagnose paddy rice health, identify varieties, and estimate plant age from a single image. Built with Python, TensorFlow, and Streamlit.

> 🤝 **Collaborative AI Project** — 2025

---

## Overview

PaddyRiceDoctor uses three Convolutional Neural Network (CNN) models to analyse a photo of a paddy rice plant and instantly return:

- **Age estimate** — days since planting (regression, min-max denormalised)
- **Variety identification** — one of 10 recognised rice varieties
- **Health status** — normal or one of 9 disease categories

Results are paired with a **Gemini 2.0 Flash** powered agronomist assistant that interprets findings and gives low-cost treatment advice tailored to the farmer's region. All predictions and conversations are persisted to a cloud Postgres database and exportable as PDF reports.

---

## Features

### 🤖 CNN Inference Pipeline
- Three `.h5` Keras models loaded with `@st.cache_resource` for performance
- Custom `DepthwiseConv2D` patch to handle legacy `groups` argument on saved models
- Automatic image pre-processing: resize to 224×224, normalise to [0, 1], rotation correction for 640×480 inputs
- **Age model** — regression output denormalised from min-max range (45–82 days)
- **Variety model** — 10-class classifier (ADT45, IR20, Ponni, Surya, RR, and more)
- **Disease model** — 10-class classifier (blast, brown_spot, tungro, hispa, bacterial_leaf_blight, and more)

### 💬 AI Agronomist Assistant (Gemini 2.0 Flash)
- Pre-built **Interpret** button — explains what the prediction means in context
- Pre-built **Advice** button — practical, low-cost prevention or treatment steps
- Free-text chat for follow-up questions
- Full conversation history maintained per prediction session
- System prompt constrains responses to paddy rice farming, region-specific, under 300 words

### 🔐 Authentication
- Farmer registration with username, email, and region
- Passwords hashed with **bcrypt**
- **JWT** session tokens (HS256, configurable expiry)
- Token verified on every page load; expired sessions redirect to login

### 📋 Prediction History
- All predictions stored in PostgreSQL (Neon serverless) with timestamps
- History page shows thumbnail, date, age, variety, and health per entry
- Per-entry **PDF export** (ReportLab) with image, results, and timestamp
- Per-entry **conversation replay** using Streamlit's `st.chat_message`
- One-click **delete** for any past prediction

### 📄 PDF Report Generation
- Generated entirely in-memory with **ReportLab** — no temporary files
- Includes the uploaded plant image, all three prediction results, and generation timestamp
- Ready for direct download via Streamlit's `download_button`

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Streamlit | Web UI framework |
| TensorFlow / Keras | CNN model inference |
| OpenCV / Pillow | Image preprocessing |
| Google Gemini 2.0 Flash (`google-genai`) | AI chat assistant |
| SQLAlchemy | ORM & database abstraction |
| PostgreSQL (Neon) | Cloud-hosted relational database |
| psycopg2-binary | PostgreSQL driver |
| bcrypt | Password hashing |
| PyJWT | JWT token creation & verification |
| ReportLab | PDF report generation |
| NumPy | Array manipulation for model input |

---

## Architecture

```
paddy_rice_web/
├── app.py                  # Entry point — page routing & auth gate
├── config.py               # All constants: DB URL, JWT, model paths,
│                           # Gemini key, prompts, class labels
├── auth.py                 # Password hashing, JWT, user lookup helpers
├── db.py                   # SQLAlchemy engine, ORM models, init_db()
├── models.py               # CNN model loading & predict_all() inference
├── utils.py                # PDF generation & Gemini chat wrapper
├── components/
│   ├── auth.py             # Streamlit login & signup UI
│   ├── predict.py          # Upload → inference → AI assistant page
│   └── history.py          # Past predictions browser
├── models/                 # Trained .h5 files (gitignored)
│   ├── age_model.h5
│   ├── variety_model.h5
│   └── label_model.h5
└── reports/
    └── images/             # Saved uploaded images (gitignored)
```

---

## Data Models

**User** — id, username (unique), email (unique), region, password_hash, created_at

**Prediction** — id, user_id (FK), image_path, predicted_age (float), predicted_var, disease_label, timestamp

**ChatLog** — id, prediction_id (FK), user_question, ai_response, timestamp

Relationships: `User` → many `Prediction` → many `ChatLog` (all cascade delete)

---

## Supported Classes

**Varieties (10)**
`ADT45`, `IR20`, `KarnatakaPonni`, `Onthanel`, `Ponni`, `Surya`, `Zonal`, `AndraPonni`, `AtchayaPonni`, `RR`

**Diseases / Health Status (10)**
`bacterial_leaf_blight`, `bacterial_leaf_streak`, `bacterial_panicle_blight`, `blast`, `brown_spot`, `dead_heart`, `downy_mildew`, `hispa`, `normal`, `tungro`

---

## Getting Started

### Prerequisites
- Python >= 3.10
- PostgreSQL database (e.g. [Neon](https://neon.tech/) free tier)
- Google Gemini API key
- Trained `.h5` model files (placed in `models/`)

### 1. Clone the repository

```bash
git clone https://github.com/Kiev2k4/paddy-rice-doctor.git
cd paddy-rice-doctor
```

### 2. Install dependencies

```bash
pip install streamlit SQLAlchemy psycopg2-binary bcrypt PyJWT \
            Pillow reportlab numpy tensorflow-cpu google-genai
```

### 3. Configure secrets

Open `config.py` and update the three values marked with comments:

```python
DB_URL         = "postgresql://user:pass@host/dbname?sslmode=require"
JWT_SECRET     = "your-secret-key"
GEMINI_API_KEY = "your-gemini-api-key"
```

### 4. Add your trained models

Place the three `.h5` files into the `models/` directory:

```
models/age_model.h5
models/variety_model.h5
models/label_model.h5
```

### 5. Run the app

```bash
streamlit run app.py
```

The app will auto-create all database tables on first run via `init_db()`.

---

## AI Prompt Design

The assistant is constrained by a system prompt injected at the start of every session:

- Persona: expert rice agronomist for the farmer's specific **region**
- Responses: bullet points, under 300 words, no unnecessary assumptions stated
- Scope: strictly paddy rice farming techniques

Two pre-built prompts reduce friction for farmers unfamiliar with AI:

| Button | Prompt template |
|---|---|
| **Interpret** | Explains what `age`, `variety`, and `label` mean for this plant |
| **Advice** | Practical low-cost prevention or treatment for the identified condition |

---

## My Contributions

- Trained CNN models for variety and disease classification using TensorFlow
- Applied image preprocessing with OpenCV for consistent model input
- Assisted in refining the training dataset
- Integrated trained models into the Streamlit dashboard alongside age estimation

---

## Author

**Hau Nguyen**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/hau-nguyen-521233254/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/Kiev2k4)
