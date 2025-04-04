# Create your views here.

import pandas as pd
from django.shortcuts import render
from .forms import CSVUploadForm
from .models import Transaction
from django.utils.dateparse import parse_datetime
from sklearn.ensemble import IsolationForest
import numpy as np

def upload_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            df = pd.read_csv(request.FILES["file"])
            for _, row in df.iterrows():
                Transaction.objects.create(
                    client_id=row["client_id"],
                    date=parse_datetime(row["date"]),
                    montant=row["montant"],
                    type_transaction=row["type_transaction"],
                    is_fraudulent=False
                )
            return render(request, "upload_success.html")
    else:
        form = CSVUploadForm()
    return render(request, "upload.html", {"form": form})

def detect_fraud():
    transactions = Transaction.objects.all()
    if transactions.count() < 10:  # Évite l'erreur si trop peu de données
        return
    
    amounts = np.array([t.montant for t in transactions]).reshape(-1, 1)
    
    model = IsolationForest(contamination=0.1)  # 10% des transactions considérées comme suspectes
    model.fit(amounts)
    
    predictions = model.predict(amounts)
    
    for transaction, pred in zip(transactions, predictions):
        if pred == -1:  # -1 indique une transaction suspecte
            transaction.is_fraudulent = True
            transaction.save()

def list_fraudulent_clients(request):
    clients_frauduleux = Transaction.objects.filter(is_fraudulent=True).values("client_id").distinct()
    return render(request, "fraud_list.html", {"clients": clients_frauduleux})