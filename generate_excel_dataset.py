import pandas as pd
import numpy as np
import random

# 1. SIMPTOMLAR VA VAZNLAR BAZASI (HTN, DM)
symptoms_data = {
    'shortness_of_breath': (0.7, 0.3), 'palpitations': (0.8, 0.3), 'dizziness': (0.7, 0.4),
    'fatigue': (0.5, 0.6), 'sweating': (0.4, 0.4), 'nausea': (0.3, 0.5),
    'arm_pain': (0.4, 0.2), 'jaw_pain': (0.4, 0.2), 'blurred_vision': (0.6, 0.6),
    'frequent_urination': (0.2, 0.95), 'dry_mouth': (0.2, 0.9), 'weight_loss': (0.2, 0.85),
    'fatigue_diabetes': (0.3, 0.8), 'blurred_vision_diabetes': (0.3, 0.85), 'slow_healing': (0.2, 0.9),
    'numbness': (0.3, 0.75), 'tingling': (0.3, 0.75), 'weakness': (0.5, 0.6),
    'insomnia': (0.6, 0.4), 'anxiety': (0.7, 0.4), 'depression': (0.5, 0.5),
    'appetite_loss': (0.3, 0.6), 'fever': (-0.2, 0.2), 'chills': (-0.2, 0.2),
    'body_pain': (0.3, 0.4), 'concentration_loss': (0.4, 0.6), 'irritability': (0.6, 0.5),
    'headache': (0.85, 0.3), 'chest_pain': (0.6, 0.5), 'thirst': (0.3, 0.95)
}

# 2. O'ZBEKCHA ISM-SHARIFLAR BAZASI
male_names = ['Ali', 'Vali', 'Hasan', 'Husan', 'Jasur', 'Sardor', 'Aziz', 'Botir', 'Rustam', 'Umid']
female_names = ['Malika', 'Nigina', 'Zuhra', 'Fotima', 'Aziza', 'Shahnoza', 'Nargiza', 'Dilnoza', 'Kamola']
last_names = ['Aliyev', 'Karimov', 'Rahimov', 'Nematov', 'Qodirov', 'Toshmatov', 'Eshmatov', 'Usmonov']
patronymics = ['Olimovich', 'Azizovich', 'Botirovich', 'Rustamovich', 'Qodirovich']

n = 100000
print(f"⏳ {n} ta bemorning ma'lumotlari shakllantirilmoqda...")
np.random.seed(42)

# 3. ASOSIY DEMOGRAFIYA VA BIOMETRIKA
gender = np.random.choice([1, 0], size=n)
birth_year = np.random.randint(1950, 2005, size=n)
age = 2024 - birth_year

height = np.where(gender == 1, np.random.normal(175, 7, n), np.random.normal(163, 6, n)).round(1)
weight = np.where(gender == 1, np.random.normal(80, 15, n), np.random.normal(68, 12, n)).round(1)
bmi = weight / ((height / 100) ** 2)

systolic_bp = np.clip(np.random.normal(115, 15, n) + (bmi - 25) * 1.5 + (age - 40) * 0.5, 80, 220).astype(int)
diastolic_bp = np.clip(systolic_bp - np.random.normal(40, 5, n), 50, 130).astype(int)
heart_rate = np.clip(np.random.normal(75, 10, n) + (bmi - 25) * 0.5, 50, 120).astype(int)
temperature = np.round(np.random.normal(36.6, 0.3, n), 1)

blood_pressure_str = [f"{sys}/{dia}" for sys, dia in zip(systolic_bp, diastolic_bp)]

base_htn_prob = 1 / (1 + np.exp(-(0.05 * (systolic_bp - 130) + 0.1 * (bmi - 25))))
base_dm_prob = 1 / (1 + np.exp(-(0.08 * (bmi - 25) + 0.05 * (age - 40))))

has_htn = (np.random.rand(n) < base_htn_prob).astype(int)
has_dm = (np.random.rand(n) < base_dm_prob).astype(int)

symptom_columns = {}
for symptom, (htn_weight, dm_weight) in symptoms_data.items():
    prob = np.random.uniform(0.01, 0.05, n)
    prob += has_htn * np.maximum(0, htn_weight) * 0.8 
    prob += has_dm * np.maximum(0, dm_weight) * 0.8
    if symptom in ['fever', 'chills']:
        has_symp = (np.random.rand(n) < prob).astype(int)
        temperature += has_symp * np.random.uniform(0.8, 1.5, n)
        symptom_columns[symptom] = has_symp
    else:
        symptom_columns[symptom] = (np.random.rand(n) < np.clip(prob, 0, 1)).astype(int)

temperature = np.round(np.clip(temperature, 35.5, 40.5), 1)

first_names = [random.choice(male_names) if g == 1 else random.choice(female_names) for g in gender]
last_names_gen = [random.choice(last_names) + ("a" if g == 0 else "") for g in gender]
patronymics_gen = [random.choice(patronymics) + ("na" if g == 0 else "") for g in gender]

# ==========================================
# 6. JADVALLARNI EXCELGA (.xlsx) SAQLASH
# ==========================================

# A) TO'LIQ BAZA UCHUN FAYL
df_full = pd.DataFrame({
    'first_name': first_names,
    'last_name': last_names_gen,
    'patronymic': patronymics_gen,
    'birth_year': birth_year,
    'gender': gender,
    'temperature': temperature,
    'blood_pressure': blood_pressure_str,
    'heart_rate': heart_rate,
    'weight': weight,
    'height': height,
})
for symp, vals in symptom_columns.items(): df_full[symp] = vals
df_full['has_htn'] = has_htn
df_full['has_dm'] = has_dm

print("⏳ 'ehr_database_100k.xlsx' fayli saqlanmoqda (100,000 qator yozish biroz vaqt oladi, kuting)...")
df_full.to_excel('ehr_database_100k.xlsx', index=False, engine='openpyxl')

# B) ML (XGBOOST) UCHUN TOZA FAYL
df_ml = pd.DataFrame({
    'age': age,
    'gender': gender,
    'weight': weight,
    'height': height,
    'temperature': temperature,
    'systolic_bp': systolic_bp,
    'diastolic_bp': diastolic_bp,
    'heart_rate': heart_rate,
})
for symp, vals in symptom_columns.items(): df_ml[symp] = vals
df_ml['has_htn'] = has_htn
df_ml['has_dm'] = has_dm

print("⏳ 'ai_training_100k.xlsx' fayli saqlanmoqda...")
df_ml.to_excel('ai_training_100k.xlsx', index=False, engine='openpyxl')

print("✅ MUVAFFAQIYATLI! Ikkita mukammal Excel (.xlsx) fayli kompyuteringizda tayyor bo'ldi.")