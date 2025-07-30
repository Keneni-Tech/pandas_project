import pandas as pd
import requests
from django.shortcuts import render

def index_view(request):
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.csv"
    df = pd.read_csv(url)

    # Optional: Filter or clean data
    df = df[["location", "total_cases", "total_deaths", "population"]]
    df = df.dropna()

    # Convert to list of dicts to pass to template
    data = df.to_dict(orient="records")

    context = {"data": data}

    return render(request, "core/home.html", context)
