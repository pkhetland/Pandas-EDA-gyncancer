import plotly.express as px
import pandas as pd
import numpy as np

""" Defining main dataset and making early adjustments
"""
# Main dataset
gyncancer_data = pd.read_csv("gyncancer_data.csv")

# Early adjustments
gyncancer_data["event.timestamp"] = pd.to_datetime(gyncancer_data["event.timestamp"])

gyncancer_data = gyncancer_data.sort_values(["patient.id", "event.timestamp"])

# Sorting out irrelevant data points
gyncancer_data = gyncancer_data[
    gyncancer_data["patient.diagnosis"] != "No cancer diagnosed"
]

gyncancer_data = gyncancer_data[
    gyncancer_data["patient.diagnosis"] != "Unspecified tumor"
]

# Generate columns with extra information
gyncancer_data["days_since_first_ts"] = (
    gyncancer_data.groupby("patient.id")
    .apply(lambda df: df["event.timestamp"] - df["event.timestamp"].min())
    .reset_index(level=1)
    .set_index("level_1")
)

gyncancer_data["all_time_days_passed"] = (
    gyncancer_data["event.timestamp"] - gyncancer_data["event.timestamp"].min()
)

gyncancer_data["month_per_patient"] = (
    (gyncancer_data["days_since_first_ts"]) / np.timedelta64(1, "M")
).astype(int)

gyncancer_data["all_time_months_passed"] = (
    (gyncancer_data["all_time_days_passed"]) / np.timedelta64(1, "M")
).astype(int)

gyncancer_data = gyncancer_data.sort_values(["all_time_months_passed"])

# Creating 'months_agg' dataframe
months_agg = gyncancer_data.groupby(["all_time_months_passed", "org.division.name"])

months_agg = months_agg.agg(
    activities_count=("event.timestamp", "count"),
    average_age=("patient.age", "mean"),
    first_ts=("event.timestamp", "min"),
    last_ts=("event.timestamp", "max"),
    months_passed=("all_time_months_passed", "max"),
    division_name=("org.division.name", "first"),
)

months_agg = months_agg.sort_values(
    ["all_time_months_passed", "activities_count"], ascending=True
)

# Creating 'patient_agg' dataframe
patient_agg = gyncancer_data.groupby(["patient.id"])

patient_agg = patient_agg.agg(
    event_count=("event.id", "count"),
    first_ts=("event.timestamp", "first"),
    last_ts=("event.timestamp", "last"),
    age=("patient.age", "mean"),
    cancer_type=("patient.diagnosis", "last"),
    start_month=("month_per_patient", "min"),
    end_month=("month_per_patient", "max"),
)

patient_agg["treatment_time"] = patient_agg["last_ts"] - patient_agg["first_ts"]
patient_agg["treatment_time_months"] = (
    patient_agg["end_month"] - patient_agg["start_month"]
)

patient_agg = patient_agg[patient_agg["treatment_time"] != "0 days"]
patient_agg = patient_agg.sort_values(["treatment_time_months"])
patient_agg = patient_agg[patient_agg["cancer_type"] != "Unspecified tumor"]
