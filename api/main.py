"""
=======================================================
  API - Classification Chat & Chien
  Modèle : EfficientNetB0 (Transfer Learning)
  Framework : FastAPI + TensorFlow/Keras
=======================================================
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from PIL import Image, UnidentifiedImageError
import io
import os
import json
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input

# =========================
# APP
# =========================
app = FastAPI(
    title="🐱🐶 Classification Chat & Chien",
    description="API de classification d'images basée sur EfficientNetB0",
    version="1.0.0"
)

# CORS — accès depuis n'importe quel navigateur
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CHEMINS
# =========================
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR     = os.path.join(BASE_DIR, "..", "model")
MODEL_PATH    = os.path.join(MODEL_DIR, "best_model.h5")
METADATA_PATH = os.path.join(MODEL_DIR, "metadata.json")

# =========================
# CONFIGURATION
# =========================
IMG_SIZE    = (224, 224)
THRESHOLD   = 0.5          # Seuil de décision binaire

# Noms des classes — remplacés par metadata.json si disponible
CLASS_NAMES = ["cat", "dog"]
CLASS_LABELS = {
    "cat": {"fr": "Chat 🐱", "emoji": "🐱", "color": "#FF6B6B"},
    "dog": {"fr": "Chien 🐶", "emoji": "🐶", "color": "#4ECDC4"},
}

# Variables globales
model    = None
metadata = {}

# =========================
# CHARGEMENT AU DÉMARRAGE
# =========================
@app.on_event("startup")
def load_model():
    global model, CLASS_NAMES, metadata

    print("=" * 50)
    print("  Démarrage de l'API Chat & Chien")
    print("=" * 50)

    # Charger metadata.json
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r") as f:
            metadata = json.load(f)
        CLASS_NAMES = metadata.get("classes", CLASS_NAMES)
        img_size    = metadata.get("img_size", list(IMG_SIZE))
        print(f"✅ Métadonnées chargées")
        print(f"   Classes     : {CLASS_NAMES}")
        print(f"   Taille img  : {img_size}")
        print(f"   Accuracy    : {metadata.get('test_accuracy', 'N/A')}")
    else:
        print(f"⚠️  metadata.json introuvable → classes par défaut : {CLASS_NAMES}")

    # Charger le modèle Keras
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Modèle introuvable : {MODEL_PATH}")
        print("   → Placez best_model.h5 dans le dossier model/")
        return

    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        # Warm-up : une prédiction factice pour initialiser
        dummy = np.zeros((1, IMG_SIZE[0], IMG_SIZE[1], 3), dtype=np.float32)
        model.predict(dummy, verbose=0)
        params = model.count_params()
        print(f"✅ Modèle EfficientNetB0 chargé")
        print(f"   Paramètres : {params:,}")
        print(f"   Chemin     : {MODEL_PATH}")
    except Exception as e:
        print(f"❌ Erreur chargement modèle : {e}")

    print("=" * 50)


# =========================
# PRÉTRAITEMENT IMAGE
# (identique au notebook)
# =========================
def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Prépare l'image pour EfficientNetB0 :
    1. Convertit en RGB
    2. Redimensionne à 224×224
    3. Applique preprocess_input EfficientNet
    4. Ajoute la dimension batch → (1, 224, 224, 3)
    """
    image     = image.convert("RGB")
    image     = image.resize(IMG_SIZE, Image.LANCZOS)
    img_array = np.array(image, dtype=np.float32)
    img_array = preprocess_input(img_array)          # normalisation [-1, 1]
    return np.expand_dims(img_array, axis=0)         # (1, 224, 224, 3)


def interpret_confidence(confidence: float) -> str:
    """Interprétation textuelle du niveau de confiance."""
    if confidence >= 0.95:
        return "Très haute"
    elif confidence >= 0.80:
        return "Haute"
    elif confidence >= 0.65:
        return "Modérée"
    else:
        return "Faible"


# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    """Informations de base sur l'API."""
    return {
        "message": "🐱🐶 API Classification Chat & Chien",
        "version": "1.0.0",
        "status":  "opérationnel" if model is not None else "modèle non chargé",
        "classes": CLASS_NAMES,
        "endpoints": {
            "health":     "GET /health",
            "model":      "GET /model",
            "prediction": "POST /predict",
        },
    }


@app.get("/health")
def health():
    """Vérification de l'état de l'API."""
    return {
        "status":        "ok",
        "model_charge":  model is not None,
        "classes":       CLASS_NAMES,
        "accuracy_test": metadata.get("test_accuracy"),
    }


@app.get("/model")
def model_info():
    """Informations sur le modèle chargé."""
    return {
        "model_charge": model is not None,
        "classes":      CLASS_NAMES,
        "img_size":     list(IMG_SIZE),
        "threshold":    THRESHOLD,
        "metadata":     metadata,
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Prédit si l'image contient un chat ou un chien.

    - **file** : image JPG / PNG / WEBP
    - Retourne la classe prédite, la confiance et les probabilités brutes
    """
    # ── Vérifications préalables ──────────────────────────────────────────────
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé. Vérifiez les logs au démarrage."
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non supporté : {file.content_type}. Envoyez une image JPG/PNG."
        )

    try:
        # ── Lecture de l'image ────────────────────────────────────────────────
        image_bytes = await file.read()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Fichier vide. Envoyez une image JPG, PNG ou WEBP valide."
            )

        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()                         # détecte les fichiers corrompus
        except UnidentifiedImageError:
            raise HTTPException(
                status_code=400,
                detail="Fichier image invalide ou format non reconnu."
            )

        # Réouvrir après verify() (verify() consomme le flux)
        image         = Image.open(io.BytesIO(image_bytes))
        original_size = image.size

        # ── Prétraitement & prédiction ────────────────────────────────────────
        processed  = preprocess_image(image)
        raw_output = model.predict(processed, verbose=0)   # shape (1, 1)

        prob_dog = float(raw_output[0][0])   # sortie sigmoid → P(chien)
        prob_cat = 1.0 - prob_dog

        pred_idx   = 1 if prob_dog >= THRESHOLD else 0
        pred_class = CLASS_NAMES[pred_idx]
        confidence = prob_dog if pred_idx == 1 else prob_cat

        # ── Réponse ──────────────────────────────────────────────────────────
        return {
            "classe":               pred_class,
            "label_fr":             CLASS_LABELS.get(pred_class, {}).get("fr", pred_class),
            "emoji":                CLASS_LABELS.get(pred_class, {}).get("emoji", ""),
            "confiance":            round(confidence, 4),
            "niveau_confiance":     interpret_confidence(confidence),
            "probabilites": {
                CLASS_NAMES[0]: round(prob_cat, 4),   # cat
                CLASS_NAMES[1]: round(prob_dog, 4),   # dog
            },
            "image_originale_size": original_size,
            "fichier":              file.filename,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {str(e)}"
        )