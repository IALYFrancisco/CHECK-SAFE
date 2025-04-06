# Étape 1 : Utiliser une image de base Python
FROM python:3.12-slim

# Étape 2 : Définir un répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3 : Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Étape 4 : Copier le reste du code de l'application dans le conteneur
COPY . /app/

# Étape 5 : Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

# Étape 6 : Exposer le port de l'application (souvent 8000 pour Gunicorn)
EXPOSE 8000

# Étape 7 : Exécuter Gunicorn pour servir l'application Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "FRAUD_DETECTION.wsgi:application"]
