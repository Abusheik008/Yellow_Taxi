# New York taxis

## Description

This project aims to compute a set of statistics from the publicly available dataset of New York taxis trips. Initially, we are only interested in Yellow taxi trips. The meaning of each field in the CSV files can be found in this [file](https://data.cityofnewyork.us/api/views/biws-g3hs/files/eb3ccc47-317f-4b2a-8f49-5a684b0b1ecc?download=true&filename=data_dictionary_trip_records_yellow.pdf).

For these trips, we would like to know:
- The average price per mile traveled by the customers of taxis.
- The distribution of payment types (how many trips are paid with each type of payment).
- The following custom indicator: (amount of tip + extra payment) / trip distance.

All these metrics should be stored as objects in a JSON file on a folder in the local file system with the following name convention `<year><month><day>_yellow_taxi_kpis.json`. For example, `"20210101_yellow_taxi_kpis.json"`.

In addition, we would like to update these metrics every day in a Linux server, given that we expect to append more data as new CSV chunks every day (you can simulate that by chunking one of the monthly available files or downloading more than one month of data).

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

1. Clone the repository.
2. Install the required packages listed in the `requirements.txt` file by running the command `pip install -r requirements.txt`.

## Usage

1. Download the Yellow taxi data from the NYC Taxi and Limousine Commission website.
2. Save the downloaded data into the `data/` directory.
3. Run the Django application by running the following command in the terminal:   
         py manage.py runserver
4. Navigate to the following URL in your browser to generate the data in JSON:
   http://localhost:8000/compute/ or http://127.0.0.1:8000/compute/
5. Once the API status becomes 200, it will return the following text: "Metrics computed and stored".
6. Navigate to the following URL in your browser to see the visualization:
   http://localhost:8000/dashboard/ or http://127.0.0.1:8000/dashboard/


## The average price per mile traveled by the customers of taxis.


    def compute_avg_price_per_mile(df: pd.DataFrame) -> float:
        """This function computes the average price per mile traveled by the customers of taxis. The input is a Pandas DataFrame and the output is a float."""
        
        # Compute the average price per mile
        df['price_per_mile'] = df['total_amount'] / df['trip_distance']
        avg_price_per_mile = df['price_per_mile'].mean()

        return avg_price_per_mile


## The distribution of payment types (how many trips are paid with each type of payment)


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


## The following custom indicator: (amount of tip + extra payment) / trip distance. 


    def compute_custom_indicator(df: pd.DataFrame) -> float:
        """This function computes a custom indicator that is the sum of the tip amount and extra payment divided by the trip distance. The input is a Pandas DataFrame and the output is a float."""
        # Compute the custom indicator
        df['custom_indicator'] = (df['tip_amount'] + df['extra']) / df['trip_distance']
        custom_indicator = df['custom_indicator'].mean()

        return custom_indicator


## Finally Storing it as JSON


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


## Scheduled Workflow

This repository contains a GitHub Actions workflow that runs a scheduled task to compute and store metrics for a Django web application.

## Schedule

The workflow is triggered by a scheduled event defined in the on field of the YAML file. In this case, the workflow is scheduled to run every day at midnight (00:00) using a cron expression:


    on:
    schedule:
        - cron: "0 0 * * *"


## Jobs

The workflow defines a single job named "build", which runs on an Ubuntu Linux runner using the latest version of the operating system:


    jobs:
    build:
        runs-on: ubuntu-latest


## Steps
The "build" job consists of several steps, each of which is responsible for a specific task.

### Checkout code
The first step checks out the repository code into the runner's file system:


    steps:
    - name: Checkout code
        uses: actions/checkout@v2
        with:
        ref: master


### Set up Python

The second step sets up the Python environment for the runner, specifying the version of Python to use:


    - name: Set up Python
        uses: actions/setup-python@v2
        with:
        python-version: '3.8'


### Install dependencies



    - name: Install dependencies
        run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt


### Run Django server

The fourth step starts the Django development server in the ./src directory of the repository:

    - name: Run Django server
        working-directory: ./src
        run: |
        python manage.py runserver 


### Send GET request

The fifth step sends a GET request to the http://127.0.0.1:8000/compute/ URL, which triggers the computation of the metrics by the Django application:


    - name: Send GET request
        run: |
        sleep 5s
        response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/compute/)
        if [[ $response -eq 200 ]]; then
            message="Metrics computed and stored"
        else
            message="Failed to compute metrics"
        fi



The step waits for 5 seconds to give the Django development server time to start up, then sends a GET request to the compute URL. If the response status code is 200, the step sets a success message to be used in the next step's commit message. Otherwise, it sets a failure message.

### Update repository

The final step updates the repository with the new metrics data, committing the changes to the repository and pushing them to the remote origin:


      current_date=$(date '+%Y-%m-%d %H:%M:%S')
      git config --global user.email "email@example.com"
      git config --global user.name "username"
      git add .
      git commit -m "Update metrics at ${current_date}: ${message}"
      git push


The step sets the current date as a variable, then sets the email and username to use for the commit. It adds all changes to the repository, commits them with a message that includes the current date and the success/failure message from the previous step, and pushes the changes to the remote origin.









