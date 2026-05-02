# 🐱🐶 Classification Chat & Chien — Deep Learning

Projet de classification d'images basé sur **EfficientNetB0** (Transfer Learning).

---

## Structure du projet

```
CatDog/
├── api/
│   ├── main.py             ← API FastAPI
│   └── requirements.txt    ← Dépendances Python
├── model/
│   ├── best_model.h5       ← Modèle Keras (à copier depuis Google Drive)
│   └── metadata.json       ← Métadonnées du modèle (classes, accuracy...)
└── static/
    └── index.html          ← Interface web
```

---

## Installation

```bash
cd api
pip install -r requirements.txt
```

---

## Lancement

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Ouvrez ensuite : **http://localhost:8000**

---

## Endpoints

| Méthode | Route      | Description                          |
|---------|------------|--------------------------------------|
| GET     | `/`        | Interface web                        |
| GET     | `/health`  | État de l'API et du modèle           |
| POST    | `/predict` | Prédiction (envoyer une image)       |

### Exemple de réponse `/predict`

```json
{
  "classe": "dog",
  "label_fr": "Chien 🐶",
  "emoji": "🐶",
  "confiance": 0.9821,
  "niveau_confiance": "Très haute",
  "probabilites": {
    "cat": 0.0179,
    "dog": 0.9821
  },
  "fichier": "mon_chien.jpg"
}
```

---

## Modèle

- Architecture : **EfficientNetB0** pré-entraîné sur ImageNet
- Fine-tuning en 2 phases (tête seule → backbone partiel)
- Entrée : images **224×224 RGB**
- Sortie : sigmoid binaire (0 = cat, 1 = dog)
- Augmentation : flip, rotation ±20°, zoom, luminosité

---

## Prérequis

Copiez ces fichiers depuis Google Drive dans le dossier `model/` :
- `best_model.h5`
- `metadata.json`
