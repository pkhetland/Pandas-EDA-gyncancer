import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats

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
unit_agg = gyncancer_data.groupby(["org.unit.name"])

unit_agg = unit_agg.agg(
    activity_name=("activity.name", "count"),
    median_activities=("patient.id", "count"),
    first_occurrence=("event.timestamp", "min"),
    last_occurrence=("event.timestamp", "max"),
    unit_name=("org.unit.name", "first"),
)

unit_agg["timespan"] = unit_agg["last_occurrence"] - unit_agg["first_occurrence"]
# unit_agg['total_median_activities_per_team'] = unit_agg.groupby(level=0)['median_activities'].transform(sum).round(1)
# unit_agg['median_percent_of_occurrences'] = (unit_agg['median_activities']/unit_agg['total_median_activities_per_team'])*100
unit_agg = unit_agg.sort_values("median_activities", ascending=False)
unit_agg = unit_agg[unit_agg["median_activities"] > 1]

# Creating 'diagnosis_agg' dataframe

diagnosis_agg = gyncancer_data.groupby(["patient.diagnosis", "patient.id"])

diagnosis_agg = diagnosis_agg.agg(
    first_ts=("event.timestamp", "first"),
    last_ts=("event.timestamp", "last"),
    event_count=("event.timestamp", "count"),
    patient_age=("patient.age", "mean"),
    start_month=("all_time_months_passed", "min"),
    end_month=("all_time_months_passed", "max"),
    patient_diagnosis=("patient.diagnosis", "last"),
)

diagnosis_agg = diagnosis_agg[
    diagnosis_agg["patient_diagnosis"] != "No cancer diagnosed"
]

diagnosis_agg["average_age"] = (
    diagnosis_agg.groupby(level=0)["patient_age"].transform("mean").round(1)
)

diagnosis_agg["age_deviation"] = (
    diagnosis_agg.groupby(level=0)["patient_age"].transform("std").round(1)
)

diagnosis_agg["treatment_time_days"] = (
    diagnosis_agg["last_ts"] - diagnosis_agg["first_ts"]
)

diagnosis_agg = diagnosis_agg[diagnosis_agg["treatment_time_days"] != "0 days"]

diagnosis_agg["treatment_time_months"] = (
    diagnosis_agg["end_month"] - diagnosis_agg["start_month"]
)

diagnosis_agg["avg_treatment_time_days"] = (
    diagnosis_agg["last_ts"].mean() - diagnosis_agg["first_ts"].mean()
)

diagnosis_agg["avg_treatment_time_months"] = (
    diagnosis_agg.groupby(level=0)["treatment_time_months"].transform("mean").round(1)
)

diagnosis_agg["treatment_time_deviation"] = (
    diagnosis_agg.groupby(level=0)["treatment_time_months"].transform("std").round(1)
)

diagnosis_agg["num_of_cases_per_diagnosis"] = diagnosis_agg.groupby(level=0)[
    "event_count"
].transform("sum")

diagnosis_agg = diagnosis_agg[diagnosis_agg["patient_diagnosis"] != "Unspecified tumor"]

diagnosis_agg = diagnosis_agg.sort_values(
    ["avg_treatment_time_months"], ascending=False
)

# Aggregating data by division and patient ID

division_by_patient_agg = gyncancer_data.groupby(["org.division.name", "patient.id"])

division_by_patient_agg = division_by_patient_agg.agg(
    first_ts=("event.timestamp", "min"),
    last_ts=("event.timestamp", "max"),
    age=("patient.age", "mean"),
    division=("org.division.name", "last"),
)

division_by_patient_agg = division_by_patient_agg[
    division_by_patient_agg["division"] != "Other"
]

# Filtering gyncancer data by top 8 teams

gyncancer_data_filtered = gyncancer_data[
    (gyncancer_data["org.unit.name"] == "Clinical chemistry")
    | (gyncancer_data["org.unit.name"] == "Radiotherapy")
    | (gyncancer_data["org.unit.name"] == "Nursing ward")
    | (gyncancer_data["org.unit.name"] == "Obstetrics and gynaecology clinic")
    | (gyncancer_data["org.unit.name"] == "Microbiology")
    | (gyncancer_data["org.unit.name"] == "Radiology")
    | (gyncancer_data["org.unit.name"] == "Pathology")
    | (gyncancer_data["org.unit.name"] == "Internal medicine clinic")
]

# Months aggregated by unit

months_agg_unit = gyncancer_data_filtered.groupby(
    ["all_time_months_passed", "org.unit.name"]
)

months_agg_unit = months_agg_unit.agg(
    activities_count=("patient.id", "count"),
    average_age=("patient.age", "mean"),
    first_ts=("event.timestamp", "min"),
    last_ts=("event.timestamp", "max"),
    months_passed=("all_time_months_passed", "mean"),
    unit_name=("org.unit.name", "first"),
    patient_count=("patient.id", "nunique"),
)

# Create normalized activities count
months_agg_unit["normalized_activities_count"] = (
    months_agg_unit["activities_count"] / months_agg_unit["patient_count"]
)
# Create mean column
months_agg_unit["activities_count_mean"] = months_agg_unit.groupby(level=1)[
    "normalized_activities_count"
].transform("mean")

# Filtering away last months
months_agg_unit = months_agg_unit.loc[0:36]

# Creating dataframes for each unit

units = [
    "Clinical chemistry",
    "Radiotherapy",
    "Nursing ward",
    "Obstetrics and gynaecology clinic",
    "Microbiology",
    "Radiology",
    "Pathology",
    "Internal medicine clinic",
]
unit_dataframes = {}
for unit in units:
    unit_dataframes[unit] = pd.DataFrame()
    unit_dataframes[unit] = months_agg_unit[months_agg_unit["unit_name"] == unit]

# Adding zscore to dataframes
for unit in units:
    unit_dataframes[unit]["zscore"] = stats.zscore(
        unit_dataframes[unit]["normalized_activities_count"]
    )

# Joining dataframes
joined_months_unit_agg = pd.concat(
    [
        unit_dataframes["Radiotherapy"],
        unit_dataframes["Clinical chemistry"],
        unit_dataframes["Nursing ward"],
        unit_dataframes["Obstetrics and gynaecology clinic"],
        unit_dataframes["Microbiology"],
        unit_dataframes["Radiology"],
        unit_dataframes["Internal medicine clinic"],
        unit_dataframes["Pathology"],
    ]
)

# Aggregating months by division

months_agg_div = gyncancer_data.groupby(
    ["all_time_months_passed", "org.division.name"]
)

months_agg_div = months_agg_div.agg(
    activities_count=("patient.id", "count"),
    average_age=("patient.age", "mean"),
    first_ts=("event.timestamp", "min"),
    last_ts=("event.timestamp", "max"),
    months_passed=("all_time_months_passed", "mean"),
    division_name=("org.division.name", "first"),
    patient_count=("patient.id", "nunique"),
)

# Create normalized activities count
months_agg_div["normalized_activities_count"] = (
    months_agg_div["activities_count"] / months_agg_div["patient_count"]
)
# Create mean column
months_agg_div["activities_count_mean"] = months_agg_div.groupby(level=1)[
    "normalized_activities_count"
].transform("mean")

# Filtering away last months
months_agg_div = months_agg_div.loc[0:36]

# Creating dataframes for each unit

divisions = [
    "Brain and senses",
    "Imaging and radiotherapy",
    "Internal medicine",
    "Laboratories",
    "Surgery",
    "Surgical sentre and intensive care",
    "Woman and child"
]
division_dataframes = {}
for division in divisions:
    division_dataframes[division] = pd.DataFrame()
    division_dataframes[division] = months_agg_div[months_agg_div["division_name"] == division]

# Adding zscore to dataframes
for division in divisions:
    division_dataframes[division]["zscore"] = stats.zscore(
        division_dataframes[division]["normalized_activities_count"]
    )

# Joining dataframes
joined_months_div_agg = pd.concat(
    [
        division_dataframes["Brain and senses"],
        division_dataframes["Imaging and radiotherapy"],
        division_dataframes["Internal medicine"],
        division_dataframes["Laboratories"],
        division_dataframes["Surgery"],
        division_dataframes["Surgical sentre and intensive care"],
        division_dataframes["Woman and child"]
    ]
)
