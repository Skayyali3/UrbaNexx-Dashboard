from flask import Flask, render_template, request
import pandas as pd
import io
import base64
import requests
import os
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt



app = Flask(__name__)

df = pd.read_csv("data/cities.csv")

iso_df = pd.read_csv("data/all.csv")

country_to_alpha2 = dict(zip(iso_df['name'], iso_df['alpha-2']))

country_to_alpha2.update({
    "UK": "GB",
    "USA": "US",
    "Palestine": "PS",
    "Russia": "RU",
    "Iran": "IR",
    "Viet Nam": "VN",
    "Korea, South": "KR",
    "Korea, North": "KP",
    "Syria": "SY",
    "Tanzania": "TZ",
    "Moldova": "MD",
    "Bolivia": "BO",
    "DRC": "CD",
    "Czechia": "CZ",
    "Laos": "LA",
    "Brunei": "BN",
    "Cabo Verde": "CV",
    "Eswatini": "SZ",
    "Micronesia": "FM",
    "Saint Kitts and Nevis": "KN",
    "Saint Lucia": "LC",
    "Saint Vincent and the Grenadines": "VC",
    "Sao Tome and Principe": "ST",
    "Timor-Leste": "TL",
    "Ivory Coast": "CI",
    "North Macedonia": "MK",
    "Burma": "MM",
    "Congo": "CG",
    "Swaziland": "SZ",
    "Cape Verde": "CV",
    "East Timor": "TL",
    "Vatican City": "VA",
    "Palestinian Territories": "PS",
    "Occupied Palestinian Territory": "PS",
    "Occupied Palestine": "PS",
    "Occupied Palestinian Territories": "PS",
    "Republic of the Congo": "CG",
    "Democratic Republic of the Congo": "CD",
    "The Gambia": "GM",
    "Bahamas": "BS",
    "Gambia": "GM",
    "Congo-Brazzaville": "CG",
    "Congo-Kinshasa": "CD",
    "Syrian Arab Republic": "SY",
    "Venezuela, RB": "VE",
    "Yemen, Rep.": "YE",
    "Iran, Islamic Rep.": "IR",
    "Korea, Dem. People's Rep.": "KP",
    "Korea, Rep.": "KR",
    "Lao PDR": "LA",
    "Russian Federation": "RU",
    "Tanzania, United Rep.": "TZ",
    "United Kingdom": "GB",
    "United States": "US",
    "PRC": "CN"
})

population_cache = {}

@app.route('/', methods=['GET'])

def dashboard():
    query = request.args.get('q', '').strip()

    if query:
        filtered = df[df['City'].str.contains(query, case=False, na=False)]
    else:
        filtered = df

    warning = None
    if request.args.get('searched') == '1' and not query:
        warning = "Please enter a city name."
    elif query and filtered.empty:
        warning = f"No data found for '{query}'."


    plot = None
    if query and not filtered.empty:
        plot = population_area_plot(filtered)

    records = filtered.to_dict(orient='records')

    for row in records:
        key = (row["City"], row["Country"])
        if key in population_cache:
            row["Population"] = population_cache[key]
            row["LivePopulation"] = True
        else:
            live_pop = fetch_population(row["City"], row["Country"])
            if live_pop:
                row["Population"] = live_pop
                row["LivePopulation"] = True
                population_cache[key] = live_pop


    return render_template('dashboard.html',tables=records,warning=warning,query=query,plot=plot)

def population_area_plot(data):
    if data.empty:
        return None
    plt.figure(figsize=(6, 4))
    plt.scatter(data['Area_km2'], data['Population'], alpha=0.7)
    plt.xlabel("Area (km²)")
    plt.ylabel("Population")
    plt.title("Population vs Area")

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    plt.close()
    img.seek(0)

    return base64.b64encode(img.read()).decode('utf-8')

GEODB_KEY = os.getenv("GEODB_API_KEY")

def fetch_population(city, country):
    code = country_to_alpha2.get(country)
    if not code:
        return None 

    url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
    headers = {
        "X-RapidAPI-Key": GEODB_KEY,
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
    }
    params = {
        "namePrefix": city,
        "countryIds": code,
        "limit": 1
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=5)
        data = r.json()
        if data["data"]:
            return data["data"][0].get("population")
    except Exception:
        pass

    return None



@app.route("/city/<city_name>")
def city_view(city_name):
    city = df[df["City"].str.lower() == city_name.lower()]
    if city.empty:
        return "City not found", 404

    return render_template("city.html", city=city.iloc[0])

if __name__ == "__main__":
    app.run(debug=True)
