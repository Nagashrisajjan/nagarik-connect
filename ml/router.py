import os
import torch
import joblib

# Dept model: you trained this with DistilBERT + label_encoder.joblib
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# Worker model: load generically so BERT/others work without mismatch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# ✅ 1) DEPARTMENT MODEL (DistilBERT)
# ==========================================
DEPT_MODEL_DIR = os.path.join(BASE_DIR, "model")

dept_tokenizer = DistilBertTokenizer.from_pretrained(DEPT_MODEL_DIR)
dept_model = DistilBertForSequenceClassification.from_pretrained(DEPT_MODEL_DIR)
dept_model.eval()

# You already saved this during training for departments
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


# ==========================================
# ✅ 2) WORKER MODEL (Auto*; uses id2label – no joblib needed)
# ==========================================
WORKER_MODEL_DIR = os.path.join(BASE_DIR, "worker_model")

# These calls will automatically pick the right classes (BERT, RoBERTa, etc.)
worker_tokenizer = AutoTokenizer.from_pretrained(WORKER_MODEL_DIR)
worker_model = AutoModelForSequenceClassification.from_pretrained(WORKER_MODEL_DIR)
worker_model.eval()

# Build id -> label mapping from the model config (e.g., {"0":"Alice","1":"Bob",...})
# If missing, fall back to sequential ids.
_worker_id2label = getattr(worker_model.config, "id2label", None)
if not _worker_id2label or not isinstance(_worker_id2label, dict):
    # Create a default mapping 0..num_labels-1 -> "LABEL_X"
    _worker_id2label = {i: f"LABEL_{i}" for i in range(worker_model.config.num_labels)}


def predict_worker(department: str, title: str, description: str) -> str | None:
    """
    Return worker label predicted from department+title+description.

    NOTE: No label_encoder.joblib is required; we use model.config.id2label.
    """
    try:
        text = f"{department} | {title} | {description}"
        inputs = worker_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = worker_model(**inputs)
            pred_id = int(torch.argmax(outputs.logits, dim=1).item())
        return _worker_id2label.get(pred_id)  # returns the worker name/label from config
    except Exception as e:
        print("Worker prediction error:", e)
        return None
