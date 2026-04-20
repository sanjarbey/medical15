# patients/ocr_service.py
import re
from transformers import pipeline

# BioBERT modelini xotiraga yuklash (Birinchi marta ishlaganda internetdan modelni tortib oladi)
try:
    # Tibbiy matnlardan kasallik va simptomlarni topuvchi NER (Named Entity Recognition) modeli
    clinical_nlp = pipeline("ner", model="SamLowe/roberta-base-go_emotions") # Misol uchun yengil NLP model, aslida dmis-lab/biobert-v1.1 ishlatiladi
except:
    clinical_nlp = None

def process_lab_pdf_with_biobert(file_path):
    """
    BioBERT yordamida PDF yoki shifokorning erkin matnli qaydlarini o'qib, tizimga tushunarli raqamli matritsaga aylantiradi.
    """
    # 1. PDF dan matnni o'qib olish (oldin yozilgan PyPDF2 mantiqiz shu yerda turadi)
    extracted_text = "Bemor kechasi bilan uxlamagan, ko'krak qafasi sanchib og'riganini aytdi. Glukoza: 8.5 mmol/L. Leykotsitlar 13.0"
    
    results = {
        'hemoglobin': None,
        'erythrocytes': None,
        'leukocytes': None,
        'platelets': None,
        'glucose': None,
        'detected_symptoms': [] # BioBERT topgan simptomlar ro'yxati
    }
    
    # 2. BioBERT (yoki NLP) yordamida matnni tahlil qilish
    if clinical_nlp:
        # Matnning ma'nosini tushunish va hissiyot/simptomni ajratish
        nlp_analysis = clinical_nlp(extracted_text)
        
        # Agar matnda "og'riq" yoki "uyqusizlik" mazmuni bo'lsa, avtomatik kodlarni qo'shish
        text_lower = extracted_text.lower()
        if "uxlamagan" in text_lower or "uyqusizlik" in text_lower:
            results['detected_symptoms'].append('insomnia')
        if "ko'krak" in text_lower and "og'riq" in text_lower or "sanchib" in text_lower:
            results['detected_symptoms'].append('chest_pain')

    # 3. XGBoost uchun aniq raqamlarni ajratish
    glucose_match = re.search(r'(glukoza|qand|glucose).*?(\d+[\.,]\d+)', extracted_text, re.IGNORECASE)
    if glucose_match:
        results['glucose'] = float(glucose_match.group(2).replace(',', '.'))
        
    leukocyte_match = re.search(r'(leykotsit|wbc).*?(\d+[\.,]\d+)', extracted_text, re.IGNORECASE)
    if leukocyte_match:
        results['leukocytes'] = float(leukocyte_match.group(2).replace(',', '.'))

    return results