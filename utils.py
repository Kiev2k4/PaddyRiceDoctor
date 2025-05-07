# utils.py

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

def save_prediction_pdf(age: float, variety: str, label: str, img: Image.Image) -> bytes:
    """
    Generate a PDF report containing:
      - Title and timestamp
      - The uploaded paddy image
      - Predicted age, variety, and health label

    Returns:
        A bytes object of the PDF, ready for Streamlit download_button.
    """
    # Create an in-memory buffer
    buffer = io.BytesIO()

    # Set up the PDF canvas
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Paddy Prediction Report")

    # Timestamp
    c.setFont("Helvetica", 10)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawString(50, height - 70, f"Generated on: {now}")

    # Prepare image for ReportLab
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="JPEG")
    img_buffer.seek(0)
    rl_img = ImageReader(img_buffer)

    # Calculate image dimensions to fit half the page height
    max_img_width  = width - 100
    img_aspect     = img.height / img.width
    img_width      = max_img_width
    img_height     = img_width * img_aspect
    if img_height > (height / 2):
        img_height = height / 2
        img_width  = img_height / img_aspect

    # Draw the image
    img_x = 50
    img_y = height - 100 - img_height
    c.drawImage(rl_img, img_x, img_y, width=img_width, height=img_height)

    # Draw the prediction text below the image
    text_x = 50
    text_y = img_y - 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(text_x, text_y,       f"Age (days): {age:.1f}")
    c.drawString(text_x, text_y - 20,  f"Variety: {variety}")
    c.drawString(text_x, text_y - 40,  f"Health: {label.capitalize()}")

    # Finalize PDF
    c.showPage()
    c.save()

    # Retrieve PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# Initialize the client
_client = genai.Client(api_key=GEMINI_API_KEY)

def gemini_chat(user_message: str, history: list[dict]) -> str:
    """
    Send the full chat history + this user message to Gemini 2.0 Flash
    and return the assistant's reply.
    """
    # 1) Record user turn
    history.append({"role": "user", "content": user_message})

    # 2) Extract just the text parts for generate_content
    #    The SDK will wrap each string as user/model based on turn ordering.
    contents = [msg["content"] for msg in history]

    # 3) Call generate_content (NOT chat_model)
    response = _client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents
    )

    # 4) Extract and record assistant turn
    reply = response.text
    history.append({"role": "assistant", "content": reply})

    return reply