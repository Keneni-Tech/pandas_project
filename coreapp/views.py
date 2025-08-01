import pandas as pd
import json
from django.shortcuts import render
from django.http import HttpResponseBadRequest

import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.express as px
from django.utils.safestring import mark_safe
import plotly.graph_objects as go


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

## eda_box_view
## second test 

def eda_boxplot_view(request):
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.csv"
    df = pd.read_csv(url)

    # Select only needed columns and drop missing values
    df = df[["location", "total_cases", "total_deaths"]].dropna()

    # Melt the DataFrame to long-form for Plotly Express
    df_melted = df.melt(id_vars="location", value_vars=["total_cases", "total_deaths"],
                        var_name="Metric", value_name="Value")

    fig = px.box(df_melted, x="Metric", y="Value", points="all", title="Total Cases and Deaths (Boxplot)")
    fig.update_layout(margin=dict(t=40, b=20))

    plot_div = fig.to_html(full_html=False)

    return render(request, 'core/boxplot.html', {'plot_div': mark_safe(plot_div)})

def eda_scatterplot_view(request):
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.csv"
    df = pd.read_csv(url)

    df = df[["location", "total_cases", "population"]].dropna()

    fig = px.scatter(
        df, x="population", y="total_cases", hover_name="location",
        title="Scatter Plot: Population vs Total Cases",
        log_x=True, log_y=True,
        labels={"population": "Population", "total_cases": "Total Cases"},
    )
    fig.update_traces(marker=dict(size=8, color='blue', opacity=0.6))
    fig.update_layout(margin=dict(t=40, b=20))

    plot_div = fig.to_html(full_html=False)

    return render(request, 'core/scatterplot.html', {'plot_div': mark_safe(plot_div)})



## first draft

def eda_boxplot_view22(request):
    # Load COVID data
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.csv"
    df = pd.read_csv(url)

    # Filter relevant numeric columns
    df = df[["location", "total_cases", "total_deaths", "population"]].dropna()

    # Create box plot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df[["total_cases", "total_deaths"]])
    plt.title("Boxplot of Total Cases and Deaths")

    # Convert to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plot_url = base64.b64encode(image_png).decode('utf-8')

    context = {'plot_url': plot_url}

    return render(request, 'core/eda_boxplot.html', context)


def eda_scatterplot_view22(request):
    # Load data
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.csv"
    df = pd.read_csv(url)
    df = df[["location", "total_cases", "total_deaths", "population"]].dropna()

    # Create scatter plot: population vs total_cases
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='population', y='total_cases', hue='location', legend=False)
    plt.xscale('log')  # Log scale for better visibility
    plt.yscale('log')
    plt.title("Scatter Plot: Population vs Total Cases")

    # Convert to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plot_url = base64.b64encode(image_png).decode('utf-8')

    context = {'plot_url': plot_url}

    return render(request, 'core/eda_scatterplot.html', context)


######################

def country_comparison_view(request):
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.csv"
    df = pd.read_csv(url)

    # Filter only countries
    df = df[df["iso_code"].str.startswith("OWID") == False]
    df = df[["location", "total_cases", "total_deaths"]].dropna()

    # Country selection from GET request
    all_countries = sorted(df["location"].unique())
    selected = request.GET.getlist("countries")

    if selected:
        df = df[df["location"].isin(selected)]

    # Build bar chart
    fig = go.Figure(data=[
        go.Bar(name='Total Cases', x=df["location"], y=df["total_cases"], marker_color='blue'),
        go.Bar(name='Total Deaths', x=df["location"], y=df["total_deaths"], marker_color='crimson'),
    ])
    fig.update_layout(
        barmode='group',
        title="COVID-19 Total Cases and Deaths by Country",
        xaxis_title="Country",
        yaxis_title="Count",
        margin=dict(t=40, b=50),
    )

    plot_div = fig.to_html(full_html=False)

    context = {
        "countries": all_countries,
        "selected": selected,
        "plot_div": mark_safe(plot_div),
    }

    return render(request, "core/compare.html", context)
