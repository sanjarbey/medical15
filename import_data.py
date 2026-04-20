import pandas as pd
import os
import django

# Django muhitini sozlash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_core.settings')
django.setup()

from ai_service.models import Visit, Patient, AIRecommendation

def import_data(file_path):
    print("Ma'lumotlar o'qilmoqda...")
    df = pd.read_csv(file_path)
    
    # 20,000 ta qatorni qayta ishlash
    for index, row in df.iterrows():
        try:
            # 1. Bemor obyektini topish yoki yaratish
            # CSV faylingizdagi 'first_name' va 'last_name' ustunlari bemorning shaxsini aniqlaydi
            patient, created = Patient.objects.get_or_create(
                first_name=row['first_name'],
                last_name=row['last_name']
            )
            
            # 2. Visit (Tashrif) obyektini yaratish
            # 'patient' maydoniga aynan 'patient' obyektining o'zi uzatiladi
            visit = Visit.objects.create(
                patient=patient,  # TO'G'RI: Bu yerda obyekt (instance) bo'lishi shart
                weight=row['weight'],
                height=row['height'],
                blood_pressure=f"{row['blood_pressure_systolic']}/{row['blood_pressure_diastolic']}",
                heart_rate=row['heart_rate'],
                temperature=row['temperature']
            )
            
            # 3. AI bashoratini yaratish
            AIRecommendation.objects.create(
                visit=visit,
                hypertension_risk=row.get('htn_risk', 0.0),
                diabetes_risk=row.get('dm_risk', 0.0),
                clinical_alert="Test rejimi xulosasi"
            )
            
            if index % 500 == 0:
                print(f"{index} ta qator import qilindi...")
                
        except Exception as e:
            print(f"Xatolik ({index}-qator): {e}")

    print("Import muvaffaqiyatli yakunlandi!")

if __name__ == "__main__":
    import_data('test_patients_20k.csv')