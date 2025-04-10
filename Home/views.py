from django.shortcuts import render
from .forms import UploadCSVForm
from django.db import connection
import pandas as pd

FRAUD_AMOUNT_THRESHOLD = 10000.0

def index(request):
    transactions = []  # Initialiser la liste des transactions
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                # 📥 Lecture du CSV
                df = pd.read_csv(csv_file)

                # 📡 Récupération des utilisateurs
                with connection.cursor() as cursor:
                    cursor.execute("SELECT client_id, nom, ville FROM users")
                    users_data = cursor.fetchall()

                users_df = pd.DataFrame(users_data, columns=['client_id', 'nom', 'ville'])

                # 🔗 Fusion des données
                merged_df = df.merge(users_df, on='client_id', how='left')

                # 🔍 Détection des fraudes
                merged_df['fraude_montant'] = merged_df['amount'] > FRAUD_AMOUNT_THRESHOLD
                merged_df['fraude_ville'] = merged_df['lieu_transaction'].str.lower() != merged_df['ville'].str.lower()

                def label_fraude(row):
                    types = []
                    if row['fraude_montant']:
                        types.append("Montant élevé")
                    if row['fraude_ville']:
                        types.append("Transaction hors ville")
                    return ", ".join(types) if types else "Aucune"

                # Ajouter une colonne "type_fraude"
                merged_df['type_fraude'] = merged_df.apply(label_fraude, axis=1)

                # Convertir le DataFrame en liste de dictionnaires
                transactions = merged_df.to_dict('records')

            except Exception as e:
                print(f"❌ Erreur lors du traitement : {e}")
    else:
        form = UploadCSVForm()

    return render(request, 'index.html', {'form': form, 'transactions': transactions})
