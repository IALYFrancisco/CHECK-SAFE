# import pandas as pd
# from django.shortcuts import render
# from .forms import UploadCSVForm

# def index(request):
#     if request.method == 'POST':
#         form = UploadCSVForm(request.POST, request.FILES)
#         if form.is_valid():
#             csv_file = request.FILES['csv_file']

#             try:
#                 df = pd.read_csv(csv_file)
#                 print("✅ Données du CSV (affichées dans la console serveur) :")
#                 print(df.to_string(index=False))  # Affiche tout proprement dans la console

#             except Exception as e:
#                 print(f"❌ Erreur lors de la lecture du CSV : {e}")
#     else:
#         form = UploadCSVForm()

#     return render(request, 'index.html', {'form': form})

# import pandas as pd
# from django.shortcuts import render
# from .forms import UploadCSVForm
# from django.db import connection  # pour interroger MariaDB

# FRAUD_AMOUNT_THRESHOLD = 1000.0  # montant élevé

# def index(request):
#     if request.method == 'POST':
#         form = UploadCSVForm(request.POST, request.FILES)
#         if form.is_valid():
#             csv_file = request.FILES['csv_file']

#             try:
#                 # Lire les transactions depuis le CSV
#                 df = pd.read_csv(csv_file)

#                 # ✅ Lire les utilisateurs depuis la base de données
#                 with connection.cursor() as cursor:
#                     cursor.execute("SELECT client_id, nom, ville FROM users")
#                     users_data = cursor.fetchall()

#                 # Transformer en DataFrame
#                 users_df = pd.DataFrame(users_data, columns=['client_id', 'nom', 'ville'])

#                 # Fusion des données CSV avec les utilisateurs
#                 merged_df = df.merge(users_df, on='client_id', how='left')

#                 # ✅ Détection des fraudes
#                 merged_df['fraude_montant'] = merged_df['amount'] > FRAUD_AMOUNT_THRESHOLD
#                 merged_df['fraude_ville'] = merged_df['lieu_transaction'].str.lower() != merged_df['ville'].str.lower()
#                 merged_df['fraude'] = merged_df['fraude_montant'] | merged_df['fraude_ville']

#                 # Filtrer les transactions frauduleuses
#                 fraudes = merged_df[merged_df['fraude']]

#                 # Afficher les noms des utilisateurs concernés dans la console
#                 utilisateurs_frauduleux = fraudes['nom'].unique()
#                 print("🚨 Utilisateurs avec des transactions frauduleuses :")
#                 for nom in utilisateurs_frauduleux:
#                     print(f"- {nom}")

#             except Exception as e:
#                 print(f"❌ Erreur lors du traitement : {e}")
#     else:
#         form = UploadCSVForm()

#     return render(request, 'index.html', {'form': form})

import pandas as pd
from django.shortcuts import render
from .forms import UploadCSVForm
from django.db import connection

FRAUD_AMOUNT_THRESHOLD = 1000.0  # seuil pour une fraude par montant

def index(request):
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
                    return ", ".join(types)

                # Ajouter une colonne "type_fraude"
                merged_df['type_fraude'] = merged_df.apply(label_fraude, axis=1)
                fraudes = merged_df[(merged_df['fraude_montant']) | (merged_df['fraude_ville'])]

                # 🖨️ Affichage des fraudes par utilisateur
                print("🚨 Fraudes détectées par utilisateur :")
                grouped = fraudes.groupby('nom')
                for nom, group in grouped:
                    print(f"\n👤 {nom} :")
                    for _, row in group.iterrows():
                        print(f" - Transaction #{row['transaction_id']} ({row['date']}): {row['type_fraude']}")

            except Exception as e:
                print(f"❌ Erreur lors du traitement : {e}")
    else:
        form = UploadCSVForm()

    return render(request, 'index.html', {'form': form})


