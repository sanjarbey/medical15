import pandas as pd
import numpy as np

def generate_exact_medical_dataset(num_samples=40000, htn_count=13315, dm_count=15750):
    print(f"Baza yaratilmoqda: Jami {num_samples} ta bemor...")
    np.random.seed(42)

    # 1. Asosiy fiziologik ma'lumotlar
    age = np.random.randint(18, 90, num_samples)
    gender = np.random.randint(0, 2, num_samples)
    height = np.random.normal(165, 10, num_samples)
    weight = np.random.normal(75, 18, num_samples)
    
    bmi = weight / ((height / 100) ** 2)

    # 2. Kasalliklarni ANIQLIK bilan taqsimlash (Eng xavfli guruhlarga berish)
    
    # Diabet (DM) taqsimoti: BMI va Yoshga qarab xavf balli hisoblanadi
    dm_risk = bmi * 1.5 + age * 0.5 + np.random.normal(0, 5, num_samples)
    target_dm = np.zeros(num_samples, dtype=int)
    # Eng yuqori ball olgan aniq 15750 kishini ajratib olamiz
    dm_indices = dm_risk.argsort()[-dm_count:] 
    target_dm[dm_indices] = 1

    # Gipertoniya (HTN) taqsimoti: Asosan Yosh va BMI ga qarab
    htn_risk = age * 0.8 + bmi * 1.2 + np.random.normal(0, 10, num_samples)
    target_htn = np.zeros(num_samples, dtype=int)
    # Eng yuqori ball olgan aniq 13315 kishini ajratib olamiz
    htn_indices = htn_risk.argsort()[-htn_count:] 
    target_htn[htn_indices] = 1

    # 3. Qon bosimi ko'rsatkichlarini Gipertoniyaga to'g'rilash
    # Kasallarda haqiqiy baland, sog'lomlarda normal bosim bo'lishini ta'minlash
    systolic_bp = np.where(target_htn == 1, 
                           np.random.normal(145, 12, num_samples), 
                           np.random.normal(115, 10, num_samples))
    
    diastolic_bp = np.where(target_htn == 1, 
                            np.random.normal(95, 8, num_samples), 
                            np.random.normal(75, 7, num_samples))
    
    temperature = np.random.normal(36.6, 0.3, num_samples)
    heart_rate = np.random.normal(80, 12, num_samples)

    # 4. Simptomlarni kasalliklar bilan kuchli bog'lash (Shifokor qaydlari uchun)
    # Diabet simptomlari
    thirst = np.where(target_dm == 1, np.random.choice([0, 1], p=[0.1, 0.9], size=num_samples), np.random.choice([0, 1], p=[0.9, 0.1], size=num_samples))
    freq_urination = np.where(target_dm == 1, np.random.choice([0, 1], p=[0.15, 0.85], size=num_samples), np.random.choice([0, 1], p=[0.95, 0.05], size=num_samples))
    blurred_vision = np.where(target_dm == 1, np.random.choice([0, 1], p=[0.3, 0.7], size=num_samples), np.random.choice([0, 1], p=[0.9, 0.1], size=num_samples))
    
    # Gipertoniya simptomlari
    headache = np.where(target_htn == 1, np.random.choice([0, 1], p=[0.2, 0.8], size=num_samples), np.random.choice([0, 1], p=[0.8, 0.2], size=num_samples))
    dizziness = np.where(target_htn == 1, np.random.choice([0, 1], p=[0.3, 0.7], size=num_samples), np.random.choice([0, 1], p=[0.9, 0.1], size=num_samples))
    
    # Umumiy simptomlar
    fatigue = np.where((target_dm == 1) | (target_htn == 1), np.random.choice([0, 1], p=[0.2, 0.8], size=num_samples), np.random.choice([0, 1], p=[0.8, 0.2], size=num_samples))

    # Jadvalni 38 ta ustun qolipida yig'ish
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
        'slow_healing': np.where(target_dm == 1, np.random.choice([0, 1], p=[0.5, 0.5], size=num_samples), 0),
        'numbness': np.where(target_dm == 1, np.random.choice([0, 1], p=[0.6, 0.4], size=num_samples), 0),
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
    
    # Saqlash jarayoni
    file_name = 'ai_training_40k.csv'
    df.to_csv(file_name, sep=';', index=False)
    
    print(f"\n✅ Muvaffaqiyatli saqlandi: {file_name}")
    print(f"--------------------------------------------------")
    print(f"📊 JAMI QATORLAR (Bemorlar): {len(df)} ta")
    print(f"🩸 Gipertoniya (HTN) bilan kasallar: {df['target_htn'].sum()} ta")
    print(f"🍩 Diabet (DM) bilan kasallar: {df['target_dm'].sum()} ta")
    
    # Faqat sog'lomlarni hisoblash
    healthy_count = len(df[(df['target_htn'] == 0) & (df['target_dm'] == 0)])
    print(f"🍀 Mutlaqo SOG'LOM bemorlar: {healthy_count} ta")
    print(f"--------------------------------------------------")

if __name__ == "__main__":
    generate_exact_medical_dataset()