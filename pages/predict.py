# pages/predict.py

import os
import streamlit as st
from PIL import Image
from datetime import datetime
from pathlib import Path

from models import predict_all
from auth import get_db, get_user_by_username
from db import Prediction, ChatLog
from utils import save_prediction_pdf, gemini_chat
from config import (
    REPORTS_DIR,
    SYSTEM_PROMPT,
    INTERPRET_PROMPT,
    ADVICE_PROMPT
)

# Prepare image storage
IMAGE_DIR = REPORTS_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

def predict_page():
    st.title("📷 Paddy Prediction")
    st.write("Upload a clear JPG image, then click **Run Prediction**.")

    # Upload & preview
    uploaded_file = st.file_uploader(
        "Choose a JPG image", type=["jpg","jpeg"], help="Only JPG/JPEG files."
    )
    img = None
    if uploaded_file:
        try:
            img = Image.open(uploaded_file)
            st.image(img, caption="✅ Uploaded Image Preview", use_container_width=True)
        except:
            st.error("⚠️ Invalid image; upload a JPG.")

    st.markdown("---")

    # Run prediction
    if st.button("🔍 Run Prediction"):
        if img is None:
            st.error("Please upload an image first.")
            return

        username = st.session_state.user
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        fname = f"{username}_{ts}.jpg"
        path  = IMAGE_DIR / fname
        img.save(path)

        st.info("Running…")
        age, variety, label = predict_all(img)

        st.markdown("### Prediction Results")
        c1, c2, c3 = st.columns(3)
        c1.metric("Age (days)", f"{age:.1f}")
        c2.metric("Variety", variety)
        c3.metric("Health", label.capitalize())

        # Save prediction
        db   = next(get_db())
        user = get_user_by_username(db, username)
        pred = Prediction(
            user_id        = user.id,
            image_path     = str(path),
            predicted_age  = float(age),
            predicted_var  = variety,
            disease_label  = label
        )
        db.add(pred); db.commit()
        st.success("Saved to history")

        # Store for chat context
        st.session_state.current_prediction = {
            "id":       pred.id,
            "age":      age,
            "variety":  variety,
            "label":    label,
            "region":   user.region
        }

        # PDF export
        pdf = save_prediction_pdf(age, variety, label, img)
        st.download_button(
            "📄 Export",
            data      = pdf,
            file_name = f"report_{ts}.pdf",
            mime      = "application/pdf"
        )

    # AI Assistant
    ctx = st.session_state.get("current_prediction")
    if not ctx:
        return

    pid     = ctx["id"]
    age     = ctx["age"]
    variety = ctx["variety"]
    label   = ctx["label"]
    region  = ctx["region"]

    with st.expander("AI Assistant"):
        # Initialize or fetch chat history,
        # but seed with an *assistant* message only
        hkey = f"history_{pid}"
        if hkey not in st.session_state:
            st.session_state[hkey] = [{
                "role":    "assistant",
                "content": SYSTEM_PROMPT.format(region=region)
            }]
        history = st.session_state[hkey]

        # Render the conversation
        for msg in history[1:]:
            st.chat_message(msg["role"]).markdown(msg["content"])
        st.markdown("---")

        # Input row: two buttons + a chat_input
        col1, col2, col3 = st.columns([1.5,1.5,7.5])
        interpret_clicked = col1.button("Interpret", key=f"interpret_{pid}")
        advice_clicked    = col2.button("Advice", key=f"advice_{pid}")
        user_q = col3.chat_input("Type your question...", key=f"chat_{pid}")

        # Determine which prompt to send
        prompt = None
        if interpret_clicked:
            prompt = INTERPRET_PROMPT.format(
                age=age, variety=variety, label=label, region=region
            )
        elif advice_clicked:
            prompt = ADVICE_PROMPT.format(
                age=age, variety=variety, label=label, region=region
            )
        elif user_q:
            prompt = user_q

        # If any action happened, send it
        if prompt:
            # Append user turn & get AI reply
            reply = gemini_chat(prompt, history)
            # Persist to DB
            db = next(get_db())
            db.add(ChatLog(
                prediction_id=pid,
                user_question=prompt,
                ai_response=reply
            ))
            db.commit()
            # Refresh so chat appears in order
            st.rerun()

        # # Clear chat
        # if st.button("Clear", key=f"clear_{pid}"):
        #     st.session_state.pop(hkey, None)
        #     st.rerun()