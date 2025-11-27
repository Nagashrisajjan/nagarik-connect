import os
import torch
import joblib

# Dept model: DistilBERT for department classification
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# DEPARTMENT MODEL (DistilBERT)
# ==========================================
DEPT_MODEL_DIR = os.path.join(BASE_DIR, "model")

dept_tokenizer = DistilBertTokenizer.from_pretrained(DEPT_MODEL_DIR)
dept_model = DistilBertForSequenceClassification.from_pretrained(DEPT_MODEL_DIR)
dept_model.eval()

dept_label_encoder = joblib.load(os.path.join(DEPT_MODEL_DIR, "label_encoder.joblib"))


def predict_department(title: str, description: str) -> str:
    """Return department string predicted from title+description."""
    try:
        text = f"{title} - {description}"
        inputs = dept_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = dept_model(**inputs)
            pred_id = int(torch.argmax(outputs.logits, dim=1).item())
        department = dept_label_encoder.inverse_transform([pred_id])[0]
        return department
    except Exception as e:
        print("Department prediction error:", e)
        return "General Department"


def predict_worker(department: str = None, title: str = None, description: str = None) -> None:
    """Worker prediction removed to save memory. Returns None."""
    return None
