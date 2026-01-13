from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)

DATA_PATH = "data/cities.csv"
df = pd.read_csv(DATA_PATH)
@app.route('/', methods=['GET'])
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

    plot = population_area_plot(filtered)

    return render_template('dashboard.html',tables=filtered.to_dict(orient='records'),warning=warning,query=query,plot=plot)

def population_area_plot(data):
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

if __name__ == "__main__":
    app.run(debug=True)
