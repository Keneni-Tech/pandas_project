import pandas as pd
import json
from django.shortcuts import render
from django.http import HttpResponseBadRequest

##########
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


def chart_view(request):
    # Load OWID/Johns Hopkins new COVID-19 cases data
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/jhu/new_cases.csv"
    try:
        df = pd.read_csv(url, index_col=False)
    except Exception as e:
        return HttpResponseBadRequest(f"Failed to fetch data: {e}")

    if 'date' not in df.columns:
        return HttpResponseBadRequest("CSV does not contain expected 'date' column")

    # Extract country list and handle missing data
    countries = sorted([col for col in df.columns if col != 'date'])

    # Get selected country or default to United States
    selected_country = request.GET.get('country', 'United States')
    if selected_country not in countries:
        selected_country = 'United States'  # Fallback

    # Parse date and filter for the selected country
    df['date'] = pd.to_datetime(df['date'])
    country_data = df[['date', selected_country]].copy()
    country_data.columns = ['Date', 'New_Cases']
    country_data['New_Cases'] = country_data['New_Cases'].fillna(0).astype(int)

    # Convert to lists for chart rendering
    dates = country_data['Date'].dt.strftime('%Y-%m-%d').tolist()
    cases = country_data['New_Cases'].tolist()

    context = {
        'selected_country': selected_country,
        'countries': countries,
        'dates': json.dumps(dates),
        'confirmed': json.dumps(cases),
    }

    return render(request, 'core/chart.html', context)


#########################################
def search_view(request):
    # Load OWID/Johns Hopkins new COVID-19 cases data
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/jhu/new_cases.csv"
    try:
        df = pd.read_csv(url, index_col=False)
    except Exception as e:
        return HttpResponseBadRequest(f"Failed to fetch data: {e}")

    if 'date' not in df.columns:
        return HttpResponseBadRequest("CSV does not contain expected 'date' column")

    countries = sorted([col for col in df.columns if col != 'date'])

    # Get search query
    query = request.GET.get('q', '').strip()

    # Try to match query to a country
    matched_country = next((c for c in countries if c.lower() == query.lower()), None)

    if not matched_country:
        return render(request, 'core/search.html', {
            'error': f"No match found for '{query}'",
            'countries': countries,
        })

    # Prepare data
    df['date'] = pd.to_datetime(df['date'])
    country_data = df[['date', matched_country]].copy()
    country_data.columns = ['Date', 'New_Cases']
    country_data['New_Cases'] = country_data['New_Cases'].fillna(0).astype(int)

    dates = country_data['Date'].dt.strftime('%Y-%m-%d').tolist()
    cases = country_data['New_Cases'].tolist()

    context = {
        'selected_country': matched_country,
        'query': query,
        'countries': countries,
        'dates': json.dumps(dates),
        'confirmed': json.dumps(cases),
    }

    return render(request, 'core/search.html', context)
