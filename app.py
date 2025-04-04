from flask import Flask, jsonify, send_from_directory
import pandas as pd
import os
from collections import defaultdict
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origin

# Load CSV File
CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrapeddata.csv")

# Function to process CSV
def process_csv():
    try:
        df = pd.read_csv(CSV_FILE_PATH)

        # Convert 'Time' column to datetime and extract years
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        df.dropna(subset=['Time'], inplace=True)  # Remove invalid dates
        df['Year'] = df['Time'].dt.year

        # Filter data from 2022 to 2025
        df = df[df['Year'].between(2022, 2025)]

        # Extract question count per tag per year
        tag_counts = defaultdict(lambda: {2022: 0, 2023: 0, 2024: 0, 2025: 0})

        for _, row in df.iterrows():
            tags = row['Tag'].split(', ') if isinstance(row['Tag'], str) else []
            year = row['Year']
            for tag in tags:
                tag_counts[tag][year] += 1

        # Sort tags by total occurrences and get the top 10
        sorted_tags = sorted(tag_counts.items(), key=lambda x: sum(x[1].values()), reverse=True)[:10]

        # Convert data into frontend-friendly format
        years = [2022, 2023, 2024, 2025]
        tags_data = [
            {"name": tag, "data": [year_data[year] for year in years]}
            for tag, year_data in sorted_tags
        ]

        return {"years": years, "tags": tags_data}

    except Exception as e:
        return {"error": str(e)}

# @app.route("/")
# def index():
#     return send_from_directory(app.static_folder, "index.html")

@app.route("/api/data")
def get_data():
    data = process_csv()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
