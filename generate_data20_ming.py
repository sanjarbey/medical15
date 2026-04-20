import pandas as pd
import random
from faker import Faker

fake = Faker()

def generate_medical_data(n=20000):
    data = []
    for _ in range(n):
        data.append({
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "age": random.randint(18, 90),
            "weight": round(random.uniform(50.0, 140.0), 2),
            "height": round(random.uniform(150.0, 200.0), 2),
            "blood_pressure_systolic": random.randint(100, 180),
            "blood_pressure_diastolic": random.randint(60, 110),
            "heart_rate": random.randint(60, 120),
            "temperature": round(random.uniform(36.0, 39.5), 1),
        })
    return pd.DataFrame(data)

# Ma'lumotlarni yaratish va faylga saqlash
df = generate_medical_data(20000)
df.to_csv('test_patients_20k.csv', index=False)
print("20 000 ta bemor ma'lumoti 'test_patients_20k.csv' fayliga saqlandi.")