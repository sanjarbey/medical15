import pandas as pd
from ai_service.models import Patient, Visit

df = pd.read_csv('test_patients_20k.csv')

for index, row in df.iterrows():
    patient = Patient.objects.create(first_name=row['first_name'], last_name=row['last_name'])
    Visit.objects.create(
        patient=patient,
        weight=row['weight'],
        bp_systolic=row['blood_pressure_systolic'],
        bp_diastolic=row['blood_pressure_diastolic'],
        heart_rate=row['heart_rate'],
        temperature=row['temperature']
    )
    if index % 1000 == 0:
        print(f"{index} ta bemor qo'shildi...")