from django.shortcuts import render
from .forms import UploadCSVForm
from django.db import connection
import pandas as pd
import json

FRAUD_AMOUNT_THRESHOLD = 10000.0

def index(request):
    transactions = []
    stats = None
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                df = pd.read_csv(csv_file)

                with connection.cursor() as cursor:
                    cursor.execute("SELECT client_id, nom, ville FROM users")
                    users_data = cursor.fetchall()

                users_df = pd.DataFrame(users_data, columns=['client_id', 'nom', 'ville'])

                merged_df = df.merge(users_df, on='client_id', how='left')

                merged_df['fraude_montant'] = merged_df['amount'] > FRAUD_AMOUNT_THRESHOLD
                merged_df['fraude_ville'] = merged_df['lieu_transaction'].str.lower() != merged_df['ville'].str.lower()

                def label_fraude(row):
                    types = []
                    if row['fraude_montant']:
                        types.append("Montant élevé")
                    if row['fraude_ville']:
                        types.append("Transaction hors ville")
                    return ", ".join(types) if types else "Aucune"

                merged_df['type_fraude'] = merged_df.apply(label_fraude, axis=1)

                transactions = merged_df.to_dict('records')

                total_transactions = len(merged_df)
                fraud_transactions = merged_df[merged_df['type_fraude'] != 'Aucune']
                fraud_count = len(fraud_transactions)
                safe_count = total_transactions - fraud_count
                fraud_percentage = (fraud_count / total_transactions) * 100 if total_transactions else 0

                total_amount = merged_df['amount'].sum()
                total_fraud_amount = fraud_transactions['amount'].sum()

                fraud_by_type = merged_df['type_fraude'].value_counts().to_dict()
                top_fraud_users = fraud_transactions['nom'].value_counts().head(5).to_dict()
                fraud_by_city = fraud_transactions['lieu_transaction'].value_counts().head(5).to_dict()

                stats = {
                    'total': total_transactions,
                    'fraudulent': fraud_count,
                    'safe': safe_count,
                    'fraud_percentage': round(fraud_percentage, 2),
                    'total_amount': round(total_amount, 2),
                    'total_fraud_amount': round(total_fraud_amount, 2),
                    'fraud_by_type': json.dumps(fraud_by_type),
                    'top_fraud_users': json.dumps(top_fraud_users),
                    'fraud_by_city': json.dumps(fraud_by_city),
                }

            except Exception as e:
                print(f"❌ Erreur lors du traitement : {e}")
    else:
        form = UploadCSVForm()

    return render(request, 'index.html', {
        'form': form,
        'transactions': transactions,
        'stats': stats
    })
