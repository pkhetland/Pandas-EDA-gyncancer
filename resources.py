import pandas as pd
import numpy as np

import datetime
import plotly.express as px

gyncancer_data = pd.read_csv('gyncancer_data.csv')
pd.options.display.max_rows = 0

gyncancer_data['event.timestamp'] = pd.to_datetime(gyncancer_data['event.timestamp'])

gyncancer_data = gyncancer_data.sort_values(['patient.id', 'event.timestamp'])

gyncancer_data['days_since_first_ts'] = (
    gyncancer_data
    .groupby('patient.id')
    .apply(
        lambda df: df['event.timestamp'] - df['event.timestamp'].min()
    )
    .reset_index(level=1)
    .set_index('level_1')
)

gyncancer_data['all_time_days_passed'] = gyncancer_data['event.timestamp'] - gyncancer_data['event.timestamp'].min()

gyncancer_data['month_per_patient'] = ((gyncancer_data['days_since_first_ts'])/np.timedelta64(1, 'M')).astype(int)

gyncancer_data['all_time_months_passed'] = ((gyncancer_data['all_time_days_passed'])/np.timedelta64(1, 'M')).astype(int)


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


density_heatmap_fig = px.density_heatmap(diagnosis_agg,
                         x='treatment_time_months',
                         y='patient_diagnosis',
                         marginal_y='histogram',
                         labels={'patient_diagnosis': 'Cancer type',
                                 'treatment_time_months': 'Treatment time (months)'}

                         )