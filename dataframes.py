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

# Creating 'unit_agg' dataframe
unit_agg = gyncancer_data.groupby(['org.unit.name'])

unit_agg = unit_agg.agg(
    activity_name = ('activity.name', 'count'),
    median_activities = ('patient.id', 'count'),
    first_occurrence = ('event.timestamp', 'min'),
    last_occurrence = ('event.timestamp', 'max'),
    unit_name = ('org.unit.name', 'first')
)

unit_agg['timespan'] = unit_agg['last_occurrence'] - unit_agg['first_occurrence']
#unit_agg['total_median_activities_per_team'] = unit_agg.groupby(level=0)['median_activities'].transform(sum).round(1)
#unit_agg['median_percent_of_occurrences'] = (unit_agg['median_activities']/unit_agg['total_median_activities_per_team'])*100
unit_agg = unit_agg.sort_values('median_activities', ascending=False)
unit_agg = unit_agg[unit_agg['median_activities'] > 1]

# Creating 'diagnosis_agg' dataframe

diagnosis_agg = gyncancer_data.groupby(['patient.diagnosis', 'patient.id'])

diagnosis_agg = diagnosis_agg.agg(
    first_ts = ('event.timestamp', 'first'),
    last_ts = ('event.timestamp', 'last'),
    event_count = ('event.timestamp', 'count'),
    patient_age = ('patient.age', 'mean'),
    start_month = ('all_time_months_passed', 'min'),
    end_month = ('all_time_months_passed', 'max'),
    patient_diagnosis = ('patient.diagnosis', 'last')
)

diagnosis_agg = diagnosis_agg[diagnosis_agg['patient_diagnosis'] != 'No cancer diagnosed']

diagnosis_agg['average_age'] = diagnosis_agg.groupby(level=0)['patient_age'].transform('mean').round(1)

diagnosis_agg['age_deviation'] = diagnosis_agg.groupby(level=0)['patient_age'].transform('std').round(1)

diagnosis_agg['treatment_time_days'] = diagnosis_agg['last_ts'] - diagnosis_agg['first_ts']

diagnosis_agg = diagnosis_agg[diagnosis_agg['treatment_time_days'] != '0 days']

diagnosis_agg['treatment_time_months'] = diagnosis_agg['end_month'] - diagnosis_agg['start_month']

diagnosis_agg['avg_treatment_time_days'] = diagnosis_agg['last_ts'].mean () - diagnosis_agg['first_ts'].mean()

diagnosis_agg['avg_treatment_time_months'] = diagnosis_agg.groupby(level=0)['treatment_time_months'].transform('mean').round(1)

diagnosis_agg['treatment_time_deviation'] = diagnosis_agg.groupby(level=0)['treatment_time_months'].transform('std').round(1)

diagnosis_agg['num_of_cases_per_diagnosis'] = diagnosis_agg.groupby(level=0)['event_count'].transform('sum')

diagnosis_agg = diagnosis_agg[diagnosis_agg['patient_diagnosis'] != 'Unspecified tumor']

diagnosis_agg = diagnosis_agg.sort_values(['avg_treatment_time_months'], ascending=False)
