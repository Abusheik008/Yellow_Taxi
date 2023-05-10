"""This section imports necessary libraries for the script. pandas is used to read and manipulate data, numpy is used for mathematical operations, json is used for reading and writing JSON files, datetime is used for getting the current date and time, and typing.Dict is used for defining the type of a dictionar"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from typing import Dict, List




def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """ This function is used to clean the input data by removing rows with missing values, filtering the yellow taxi trips, and filtering trips with non-positive fare amounts, distances, and durations. The input is a Pandas DataFrame and the output is also a Pandas DataFrame."""

    # Remove rows with missing values
    df = df.dropna()

    # Filter the yellow taxi trips
    df = df[df['VendorID'] == 1]

    # Filter trips with a non-positive fare amount
    df = df[df['fare_amount'] > 0]

    # Filter trips with a non-positive distance
    df = df[df['trip_distance'] > 0]



    return df


def compute_avg_price_per_mile(df: pd.DataFrame) -> float:
    """This function computes the average price per mile traveled by the customers of taxis. The input is a Pandas DataFrame and the output is a float."""
    
    # Compute the average price per mile
    df['price_per_mile'] = df['total_amount'] / df['trip_distance']
    avg_price_per_mile = df['price_per_mile'].mean()

    return avg_price_per_mile



def compute_payment_type_counts(df: pd.DataFrame) -> Dict[str, List[int]]:
    """This function computes the distribution of payment types (how many trips are paid with each type of payment). The input is a Pandas DataFrame and the output is a dictionary with string keys and integer values.
    1= Credit card
    2= Cash
    3= No charge
    4= Dispute
    5= Unknown
    6= Voided trip """
    # Compute the distribution of payment types and group by payment type
    payment_type_counts = df.groupby('payment_type')['payment_type'].count().to_dict()

    return payment_type_counts



def compute_custom_indicator(df: pd.DataFrame) -> float:
    """This function computes a custom indicator that is the sum of the tip amount and extra payment divided by the trip distance. The input is a Pandas DataFrame and the output is a float."""
    # Compute the custom indicator
    df['custom_indicator'] = (df['tip_amount'] + df['extra']) / df['trip_distance']
    custom_indicator = df['custom_indicator'].mean()

    return custom_indicator


def compute_metrics(df: pd.DataFrame) -> None:
    # Clean the data
    df = clean_data(df)

    # Compute the metrics
    avg_price_per_mile = compute_avg_price_per_mile(df)
    payment_type_counts = compute_payment_type_counts(df)
    custom_indicator = compute_custom_indicator(df)

    # Create a dictionary with the computed metrics
    metrics = {
        'average_price_per_mile': avg_price_per_mile,
        'payment_type_counts': payment_type_counts,
        'custom_indicator': custom_indicator,
    }

    # Store the metrics in a JSON file
    now = datetime.now().strftime('%Y%m%d')
    file_name = f'data_json/{now}_yellow_taxi_kpis.json'
    with open(file_name, 'w') as f:
        json.dump(metrics, f)
