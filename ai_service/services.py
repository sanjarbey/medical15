import os
import joblib
import pandas as pd
from django.conf import settings

def get_ai_prediction(visit_symptom):
    """
    Bemor ma'lumotlari, shifokor qaydlari va belgilangan simptomlar asosida
    Gipertoniya (HTN) va Diabet (DM) xavfini hisoblovchi AI funksiyasi.
    """
    # Xatolik yuz berganda dastur qulamasligi uchun standart qiymatlar
    htn_prob = 0.0
    dm_prob = 0.0

    try:
        # 1. Tayyorlangan AI modellarini va ustunlarni yuklash
        htn_path = os.path.join(settings.BASE_DIR, 'xgboost_htn_model.pkl')
        dm_path = os.path.join(settings.BASE_DIR, 'xgboost_dm_model.pkl')
        features_path = os.path.join(settings.BASE_DIR, 'feature_cols.pkl')

        model_htn = joblib.load(htn_path)
        model_dm = joblib.load(dm_path)
        feature_cols = joblib.load(features_path)

        visit = visit_symptom.visit
        patient = visit.patient

        # 2. Qon bosimini tekshirish va xavfsiz ajratish
        bp_data = visit_symptom.blood_pressure
        # Agar VisitSymptom da bosim bo'lmasa, Visit modelidan qaraymiz
        if not bp_data and hasattr(visit, 'blood_pressure'):
            bp_data = visit.blood_pressure
            
        if bp_data and isinstance(bp_data, str) and '/' in bp_data:
            try:
                systolic, diastolic = map(int, bp_data.split('/'))
            except ValueError:
                systolic, diastolic = 120, 80 # Format xato bo'lsa standart bosim
        else:
            systolic, diastolic = 120, 80

        # 3. Asosiy fiziologik ma'lumotlarni yig'ish
        data = {
            'age': 2026 - patient.date_of_birth.year,
            'gender': 1 if patient.gender == 'Erkak' else 0,
            'weight': float(visit.weight or 0),
            'height': float(visit.height or 0),
            'temperature': float(visit.temperature or 36.6),
            'systolic_bp': float(systolic),
            'diastolic_bp': float(diastolic),
            'heart_rate': float(visit.heart_rate or 80),
        }

        # 4. Tabiiy tilni qayta ishlash (NLP) - Matn va Chekbokslarni birlashtirish
        notes = (visit.doctor_notes or "").lower()
        
        # Bemor sahifasida (chekboks orqali) belgilangan barcha simptomlarni bazadan tortish
        checked_symptoms_text = ""
        for vs in visit.visitsymptom_set.all():
            try:
                if hasattr(vs, 'symptom') and vs.symptom:
                    checked_symptoms_text += str(vs.symptom).lower() + " "
                elif hasattr(vs, 'symptom_id'):
                    checked_symptoms_text += str(vs.symptom_id).lower() + " "
            except Exception:
                checked_symptoms_text += str(vs).lower() + " "

        # Erkin matn (Doctor notes) va belgilangan pichkalarni bitta umumiy matnga birlashtiramiz
        combined_text = notes + " " + checked_symptoms_text
        
        # Simptomlarni aniqlash (Ingliz va o'zbekcha nomlarni ham ushlab oladi)
        # Diabet simptomlari
        data['thirst'] = 1 if any(w in combined_text for w in ["chanqash", "og'iz", "suv", "thirst"]) else 0
        data['frequent_urination'] = 1 if any(w in combined_text for w in ["siyish", "poliuriya", "urination"]) else 0
        data['blurred_vision'] = 1 if any(w in combined_text for w in ["ko'z", "xiralashishi", "vision"]) else 0
        
        # Gipertoniya simptomlari
        data['headache'] = 1 if any(w in combined_text for w in ["bosh", "migren", "headache"]) else 0
        data['dizziness'] = 1 if any(w in combined_text for w in ["aylan", "girdob", "dizziness"]) else 0
        
        # Umumiy simptomlar
        data['fatigue'] = 1 if any(w in combined_text for w in ["holsizlik", "charchoq", "fatigue", "darmonsizlik"]) else 0

        # Diagnostika uchun terminalga (VS Code ekraniga) chiqarish
        print("\n--- AI DIAGNOSTIKA INFO ---")
        print(f"Klinik ma'lumot: Yosh={data['age']}, Bosim={systolic}/{diastolic}, Vazn={data['weight']}kg")
        print(f"AI o'qiyotgan matn: '{combined_text.strip()}'")
        print(f"Topilgan simptomlar: Chanqash={data['thirst']}, Siyish={data['frequent_urination']}, "
              f"Bosh og'rig'i={data['headache']}, Holsizlik={data['fatigue']}")

        # 5. Model kutayotgan barcha 38 ta ustunni to'ldirish
        df = pd.DataFrame([data])
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0  # Biz kiritmagan ustunlarni 0 (yo'q) deb qabul qilish

        # Ustunlarni AI modeli o'qitilgan aniq tartibda joylashtirish
        input_df = df[feature_cols]

        # 6. Ehtimollikni (Bashoratni) hisoblash
        htn_pred = model_htn.predict_proba(input_df)
        dm_pred = model_dm.predict_proba(input_df)

        htn_prob = float(htn_pred[0][1])
        dm_prob = float(dm_pred[0][1])

        print(f"Bashorat natijasi: Gipertoniya(HTN) = {htn_prob*100:.2f}%, Diabet(DM) = {dm_prob*100:.2f}%")
        print("---------------------------\n")

    except Exception as e:
        print(f"AI XATOLIGI (get_ai_prediction): {e}")

    # Foiz ko'rinishida yaxlitlab qaytarish (masalan: 0.854 -> 85.4)
    return round(htn_prob * 100, 2), round(dm_prob * 100, 2)