# Create your views here.

import pandas as pd
from django.shortcuts import render
from .forms import CSVUploadForm
from .models import Transaction
from django.utils.dateparse import parse_datetime

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
