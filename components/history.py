# pages/history.py

import os
import streamlit as st
from PIL import Image

from auth import get_db, get_user_by_username
from db import Prediction, ChatLog
from utils import save_prediction_pdf

def history_page():
    """
    Display the logged-in user’s past predictions.
    For each prediction:
      - Show thumbnail, details, PDF download, and Delete.
      - Provide a 'View Conversation' expander rendering the chat history.
    """
    st.title("🕘 Prediction History")
    username = st.session_state.user

    # Fetch predictions
    db   = next(get_db())
    user = get_user_by_username(db, username)
    preds = (
        db.query(Prediction)
          .filter(Prediction.user_id == user.id)
          .order_by(Prediction.timestamp.desc())
          .all()
    )

    if not preds:
        st.info("You have no past predictions.")
        return

    for pred in preds:
        st.markdown("---")

        # Row: thumbnail | details | PDF | Delete
        col1, col2, col3, col4 = st.columns([1,4,1,1])

        # Thumbnail
        if os.path.exists(pred.image_path):
            img = Image.open(pred.image_path)
            col1.image(img, width=100)
        else:
            col1.write("🖼️ Missing image")

        # Details
        col2.markdown(f"**Date:** {pred.timestamp:%Y-%m-%d %H:%M:%S}")
        col2.markdown(f"**Age (days):** {pred.predicted_age:.1f}")
        col2.markdown(f"**Variety:** {pred.predicted_var}")
        col2.markdown(f"**Health:** {pred.disease_label.capitalize()}")

        # PDF export
        if os.path.exists(pred.image_path):
            pdf_bytes = save_prediction_pdf(
                age=pred.predicted_age,
                variety=pred.predicted_var,
                label=pred.disease_label,
                img=Image.open(pred.image_path)
            )
            col3.download_button(
                "📄 PDF",
                data=pdf_bytes,
                file_name=f"report_{pred.id}.pdf",
                mime="application/pdf",
                key=f"dl_{pred.id}"
            )
        else:
            col3.write("")

        # Delete
        if col4.button("Delete", key=f"del_{pred.id}"):
            db.delete(pred)
            db.commit()
            st.rerun()

        # ───────────────────────────────────────────────────────────────
        # View Conversation expander
        # ───────────────────────────────────────────────────────────────
        exp = st.expander("💬 View Conversation", expanded=False)

        # Fetch chat logs in chronological order
        chats = (
            db.query(ChatLog)
              .filter(ChatLog.prediction_id == pred.id)
              .order_by(ChatLog.timestamp.asc())
              .all()
        )

        with exp:
            if not chats:
                st.info("No conversation recorded for this prediction.")
            else:
                for log in chats:
                    # User question
                    st.chat_message("user").markdown(log.user_question)
                    # AI response
                    st.chat_message("assistant").markdown(log.ai_response)
