# Publication sur GitHub

Ce projet est une API FastAPI. GitHub sert a publier le code source, mais GitHub Pages ne peut pas executer cette API Python.

## 1. Verifier les fichiers

Depuis le dossier du projet :

```powershell
cd "C:\Users\dell\Downloads\catdog_project (3)\catdog"
git status
```

Les dossiers/fichiers suivants sont ignores volontairement :

- `api/.venv/`
- `api/__pycache__/`
- `*.log`
- `.idea/`
- `*.bak`
- `*.pkl`

## 2. Premier commit

```powershell
git add .
git commit -m "Initial FastAPI cat dog classifier"
```

Si Git demande ton nom et ton email :

```powershell
git config --global user.name "Ton Nom"
git config --global user.email "ton-email@example.com"
git commit -m "Initial FastAPI cat dog classifier"
```

## 3. Creer le repository sur GitHub

Sur GitHub, cree un nouveau repository, par exemple :

```text
catdog-api
```

Ne coche pas `Add a README`, car le projet en a deja un.

## 4. Envoyer vers GitHub

Remplace `catdog-api` par le nom de ton repository si besoin :

```powershell
git branch -M main
git remote add origin https://github.com/annagueye/catdog-api.git
git push -u origin main
```

## 5. Lancer l'API en local

```powershell
cd "C:\Users\dell\Downloads\catdog_project (3)\catdog\api"
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Routes

```text
GET  /
GET  /health
GET  /model
POST /predict
```

Exemple POST :

```powershell
curl.exe -X POST "http://localhost:8000/predict" -F "file=@C:\Users\dell\Pictures\image.jpg"
```

## Pour heberger l'API en ligne

Utilise un service qui execute Python, par exemple Render, Railway ou Hugging Face Spaces. GitHub Pages ne suffit pas pour FastAPI.
