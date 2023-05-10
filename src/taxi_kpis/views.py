from django.http import HttpResponse
from django.shortcuts import render
from taxi_kpis.analytics import compute_metrics
import os
import json
import urllib.request
import pandas as pd
from datetime import datetime

def find_current_month():
    current_date = datetime.now()
    current_month_date = datetime(current_date.year, current_date.month, 1)
    month_year = current_month_date.strftime('%Y-%m')
    
    return month_year

def compute(request):
    # Define the download URL
    # month_year = find_current_month()
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-02.parquet'

    # Define the folder where the data will be stored
    folder_path = 'data'

    # Check if the folder exists, otherwise create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Extract the year and month from the URL and create the filename
    year_month = url.split('_')[-1].split('.')[0]
    file_name = f'yellow_tripdata_{year_month}.parquet'
    path = os.path.join(folder_path, file_name)

    # Check if the file for the current month exists
    if os.path.exists(path):
        # Read the file and check if it's up to date
        df = pd.read_parquet(path)
        last_date = pd.to_datetime(df['tpep_pickup_datetime'].max())
        current_date = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))
        if last_date.date() >= current_date.date():
            # Data is up to date
            return HttpResponse('Data is up to date')
        else:
            # Data is outdated, download the new file
            os.remove(path)  # remove the old file
            urllib.request.urlretrieve(url, path)
            df = pd.read_parquet(path)
    else:
        # File for current month doesn't exist, download it
        urllib.request.urlretrieve(url, path)
        df = pd.read_parquet(path)

    # Compute the metrics and store them in a JSON file
    compute_metrics(df)

    return HttpResponse('Metrics computed and stored')


def dashboard(request):
    # Get the data from JSON file
    with open(r'D:\My Learnings\Yellow_taxi\kpis\data_json\20230510_yellow_taxi_kpis.json') as f:
        data = json.load(f)

    # Pass the data to the template
    context = {
        'data': data,
    }

    # Render the template with the context data
    return render(request, 'dashboard.html', context)
