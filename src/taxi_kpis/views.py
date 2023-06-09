from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from taxi_kpis.analytics import compute_metrics
import os
import json
import urllib.request
import pandas as pd
from datetime import datetime

def find_current_month():
    """
    Returns the current month in the format YYYY-MM.

    Returns:
        str: A string representing the current month in the format YYYY-MM.
    """
    current_date = datetime.now()
    current_month_date = datetime(current_date.year, current_date.month, 1)
    month_year = current_month_date.strftime('%Y-%m')
    
    return month_year

def compute(request):

    """
    Downloads the yellow taxi trip data for the current month, checks if the data is up-to-date,
    computes metrics, and stores them in a JSON file.

    Args:
        request: A Django request object.

    Returns:
        HttpResponse: A Django HTTP response indicating if the data is up-to-date or if the
                       metrics were computed and stored successfully.
    """

    # Define the download URL
    month_year = find_current_month()
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_year}.parquet'

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
            print(";;;;;",url, path)
            os.remove(path)  # remove the old file
            urllib.request.urlretrieve(url, path)
            df = pd.read_parquet(path)
    else:
        # File for current month doesn't exist, download it
        try:
            urllib.request.urlretrieve(url, path)
            df = pd.read_parquet(path)
            # Compute the metrics and store them in a JSON file
            compute_metrics(df)
        except:
            print(f"This Month data is not available {month_year}")        

    return HttpResponse('Metrics computed and stored')

def home(request):
    return render(request, 'dashboard.html')



def dashboard(request):
    """
    Renders a dashboard with aggregated metrics based on the data stored in JSON files.

    Args:
        request: A Django request object.

    Returns:
        HttpResponse: A Django HTTP response containing the rendered dashboard template.
    """
    # Define the directory where the JSON files are stored
    json_dir = 'taxi_kpis/data_json'

    # Initialize variables to store aggregated metrics
    total_avg_price_per_mile = 0
    total_payment_type_counts = {"1": 0, "2": 0, "3": 0, "4": 0}
    total_custom_indicator = 0

    # Iterate over all JSON files in the directory
    for file_name in os.listdir(json_dir):
        if file_name.endswith('.json'):
            # Load the JSON data from the file
            with open(os.path.join(json_dir, file_name)) as f:
                data = json.load(f)

            # Add the metrics from the current file to the running totals
            total_avg_price_per_mile += data["average_price_per_mile"]
            for payment_type, count in data["payment_type_counts"].items():
                total_payment_type_counts[payment_type] += count
            total_custom_indicator += data["custom_indicator"]

    # Calculate the average metrics across all files
    num_files = len([f for f in os.listdir(json_dir) if f.endswith('.json')])
    avg_avg_price_per_mile = total_avg_price_per_mile / num_files
    avg_payment_type_counts = {payment_type: count / num_files for payment_type, count in total_payment_type_counts.items()}
    avg_custom_indicator = total_custom_indicator / num_files

    # Render the template with the aggregated metrics
    context = {
        'avg_price_per_mile': avg_avg_price_per_mile,
        'payment_type_counts': avg_payment_type_counts,
        'custom_indicator': avg_custom_indicator
    }

    print(context,"----")

    return JsonResponse(context)
