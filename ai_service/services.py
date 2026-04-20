from ehr_core import settings
import joblib, os
import pandas as pd

def get_ai_prediction(visit):
    # 1. MODELLARNI YUKLASH (Mutlaq manzil orqali xatolikni oldini olamiz)
    htn_path = os.path.join(settings.BASE_DIR, 'xgboost_htn_model.pkl')
    dm_path = os.path.join(settings.BASE_DIR, 'xgboost_dm_model.pkl')
    features_path = os.path.join(settings.BASE_DIR, 'feature_cols.pkl')
    model_htn = joblib.load(htn_path)
    model_dm = joblib.load(dm_path)
    feature_cols = joblib.load(features_path)
    
    # Ma'lumotlarni yig'ish
    bp = visit.blood_pressure.split('/')
    data = {
        'age': 2026 - visit.patient.date_of_birth.year,
        'gender': 1 if visit.patient.gender == 'Erkak' else 0,
        'weight': float(visit.weight),
        'height': float(visit.height),
        'temperature': float(visit.temperature),
        'systolic_bp': float(bp[0]),
        'diastolic_bp': float(bp[1]),
        'heart_rate': float(visit.heart_rate),
    }
    
    # Qolgan simptomlarni 0 deb belgilash
    for col in feature_cols:
        if col not in data:
            data[col] = 0
            
    # Doktor yozuvlariga qarab simptomlarni aktivlashtirish
    notes = visit.doctor_notes.lower()
    if "bosh og'ri" in notes: 
        data['headache'] = 1
    if 'chanqash' in notes: data['thirst'] = 1
    
    # Bashorat qilish
    input_df = pd.DataFrame([data])[feature_cols]
    htn_prob = model_htn.predict_proba(input_df)[0][1]
    dm_prob = model_dm.predict_proba(input_df)[0][1]
    
    return htn_prob * 100, dm_prob * 100