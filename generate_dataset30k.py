import pandas as pd
import numpy as np

def generate_medical_dataset(num_samples=30000):
    print(f"Baza yaratilmoqda: {num_samples} ta bemor...")
    np.random.seed(42)

    # Asosiy fiziologik ko'rsatkichlar
    age = np.random.randint(18, 90, num_samples)
    gender = np.random.randint(0, 2, num_samples) # 1 - Erkak, 0 - Ayol
    height = np.random.normal(165, 10, num_samples) # o'rtacha 165 sm
    weight = np.random.normal(75, 18, num_samples)  # o'rtacha 75 kg
    temperature = np.random.normal(36.6, 0.3, num_samples)
    heart_rate = np.random.normal(80, 12, num_samples)

    # Tana massasi indeksi (BMI)
    bmi = weight / ((height / 100) ** 2)

    # Qon bosimini yosh va BMI ga bog'lab generatsiya qilish
    systolic_bp = 100 + (age * 0.3) + (bmi * 0.6) + np.random.normal(0, 10, num_samples)
    diastolic_bp = 65 + (age * 0.15) + (bmi * 0.4) + np.random.normal(0, 8, num_samples)

    # MAQSADLI O'ZGARUVCHILAR (Target Variables - Kasallik mavjudligi)
    # Gipertoniya (HTN): Sistolik > 140 yoki Diastolik > 90 bo'lsa
    target_htn = np.where((systolic_bp >= 140) | (diastolic_bp >= 90), 1, 0)
    
    # Qandli Diabet (DM): BMI > 30 va Yosh > 45 bo'lganda ehtimol yuqori
    dm_prob = (bmi > 30).astype(int) + (age > 45).astype(int)
    target_dm = np.where(dm_prob >= 1, np.random.choice([0, 1], p=[0.3, 0.7], size=num_samples), 0)

    # Shovqin qo'shish (100% ideal bo'lmasligi uchun tabiat qonuniyatlariga moslash)
    target_htn = np.logical_xor(target_htn, np.random.rand(num_samples) < 0.05).astype(int)
    target_dm = np.logical_xor(target_dm, np.random.rand(num_samples) < 0.03).astype(int)

    # SIMPTOMLARNI KASALLIKKA BOG'LASH (NLP uchun)
    # Diabet simptomlari
    thirst = np.where(target_dm == 1, np.random.choice([0, 1], p=[0.2, 0.8], size=num_samples), np.random.choice([0, 1], p=[0.9, 0.1], size=num_samples))
    freq_urination = np.where(target_dm == 1, np.random.choice([0, 1], p=[0.3, 0.7], size=num_samples), np.random.choice([0, 1], p=[0.95, 0.05], size=num_samples))
    blurred_vision = np.where(target_dm == 1, np.random.choice([0, 1], p=[0.4, 0.6], size=num_samples), np.random.choice([0, 1], p=[0.9, 0.1], size=num_samples))
    
    # Gipertoniya simptomlari
    headache = np.where(target_htn == 1, np.random.choice([0, 1], p=[0.3, 0.7], size=num_samples), np.random.choice([0, 1], p=[0.8, 0.2], size=num_samples))
    dizziness = np.where(target_htn == 1, np.random.choice([0, 1], p=[0.4, 0.6], size=num_samples), np.random.choice([0, 1], p=[0.9, 0.1], size=num_samples))
    
    # Umumiy simptom (Ikkala kasallikda ham uchrashi mumkin)
    fatigue = np.where((target_dm == 1) | (target_htn == 1), np.random.choice([0, 1], p=[0.3, 0.7], size=num_samples), np.random.choice([0, 1], p=[0.8, 0.2], size=num_samples))

    # Jadvalni yig'ish (Sizdagi 38 ta ustun tartibi bo'yicha)
    data = {
        'age': np.round(age).astype(int),
        'gender': gender,
        'weight': np.round(weight, 1),
        'height': np.round(height, 1),
        'temperature': np.round(temperature, 1),
        'systolic_bp': np.round(systolic_bp, 1),
        'diastolic_bp': np.round(diastolic_bp, 1),
        'heart_rate': np.round(heart_rate).astype(int),
        'shortness_of_breath': np.random.choice([0, 1], p=[0.85, 0.15], size=num_samples),
        'palpitations': np.random.choice([0, 1], p=[0.9, 0.1], size=num_samples),
        'dizziness': dizziness,
        'fatigue': fatigue,
        'sweating': np.random.choice([0, 1], p=[0.9, 0.1], size=num_samples),
        'nausea': np.random.choice([0, 1], p=[0.95, 0.05], size=num_samples),
        'arm_pain': 0, 'jaw_pain': 0,
        'blurred_vision': blurred_vision,
        'frequent_urination': freq_urination,
        'dry_mouth': thirst,
        'weight_loss': np.random.choice([0, 1], p=[0.95, 0.05], size=num_samples),
        'fatigue_diabetes': fatigue,
        'blurred_vision_diabetes': blurred_vision,
        'slow_healing': np.where(target_dm == 1, np.random.choice([0, 1], p=[0.6, 0.4], size=num_samples), 0),
        'numbness': np.where(target_dm == 1, np.random.choice([0, 1], p=[0.7, 0.3], size=num_samples), 0),
        'tingling': 0, 'weakness': 0, 'insomnia': 0, 'anxiety': 0, 'depression': 0,
        'appetite_loss': 0, 'fever': 0, 'chills': 0, 'body_pain': 0, 'concentration_loss': 0,
        'irritability': 0,
        'headache': headache,
        'chest_pain': 0,
        'thirst': thirst,
        'target_htn': target_htn,
        'target_dm': target_dm
    }

    df = pd.DataFrame(data)
    
    # Saqlash
    file_name = 'ai_training_30k.csv'
    df.to_csv(file_name, sep=';', index=False)
    print(f"Muvaffaqiyatli saqlandi: {file_name}")
    print(f"Jami ustunlar: {len(df.columns)}")
    print(f"Gipertoniya bilan bemorlar: {df['target_htn'].sum()} ta")
    print(f"Diabet bilan bemorlar: {df['target_dm'].sum()} ta")

if __name__ == "__main__":
    generate_medical_dataset()