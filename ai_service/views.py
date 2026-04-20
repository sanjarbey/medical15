# ai_service/views.py ichidagi train_ai_model_view funksiyasini quyidagicha o'zgartiring:
import os
import pandas as pd
import joblib
import xgboost as xgb # YANGI: XGBoost kutubxonasi
from django.shortcuts import render, redirect
from django.contrib import messages
from patients.views import get_user_role
from django.contrib.auth.decorators import login_required 
@login_required
def train_ai_model_view(request):
    role = get_user_role(request.user)
    
    # FAQAT Super Admin yoki Boshqaruvchilar modelni qayta o'qita oladi
    if role not in ['Super Admin', 'Moderator']:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Xatolik! Sizda AI modelini o'qitish huquqi yo'q.")

    if request.method == 'POST' and 'dataset_file' in request.FILES:
        excel_file = request.FILES['dataset_file']
        
        try:
            # 1. Yuklangan CSV faylni o'qish (Sizning faylingiz ";" bilan ajratilgan)
            if excel_file.name.endswith('.csv'):
                df = pd.read_csv(excel_file, sep=';')
            else:
                df = pd.read_excel(excel_file)

            # 2. MA'LUMOTLARNI BIZNING TIZIMGA MOSLASHTIRISH (PREPROCESSING)
            
            # A) Bo'y (sm) va vazn (kg) orqali Tana massasi indeksini (BMI) hisoblash
            df['bmi'] = df['weight'] / ((df['height'] / 100) ** 2)
            
            # B) Qon bosimi ustunini bizning formatga o'tkazish
            df['systolic_bp'] = df['ap_hi']
            
            # C) Bu datasetda yurak urishi (heart_rate) kiritilmagan. Model xato bermasligi uchun hammaga o'rtacha 75 kiritamiz
            df['heart_rate'] = 75
            
            # D) Glukoza (1: normal, 2: yuqori, 3: juda yuqori) ni haqiqiy mmol/L qiymatlarga o'giramiz
            df['glucose'] = df['gluc'].map({1: 5.0, 2: 7.5, 3: 11.0})
            
            # E) Natijaviy kasalliklarni aniqlash
            df['has_htn'] = df['cardio'] # Yurak kasalligi borligi (1 yoki 0)
            df['has_dm'] = df['gluc'].apply(lambda x: 1 if x > 1 else 0) # Glukoza normadan baland bo'lsa diabet = 1

            # 3. XGBoost uchun kerakli ustunlarni ajratib olish
            X = df[['bmi', 'systolic_bp', 'heart_rate', 'glucose']]
            y_htn = df['has_htn'] 
            y_dm = df['has_dm']   

            # 4. Modelni o'qitish (XGBoost)
            model_htn = xgb.XGBClassifier(n_estimators=150, learning_rate=0.05, max_depth=5, random_state=42, eval_metric='logloss')
            model_dm = xgb.XGBClassifier(n_estimators=150, learning_rate=0.05, max_depth=5, random_state=42, eval_metric='logloss')
            
            model_htn.fit(X, y_htn)
            model_dm.fit(X, y_dm)

            # Modelni xotiraga saqlash
            model_path = os.path.dirname(__file__)
            joblib.dump(model_htn, os.path.join(model_path, 'htn_model.pkl'))
            joblib.dump(model_dm, os.path.join(model_path, 'dm_model.pkl'))

            messages.success(request, "🎉 Tabriklaymiz! XGBoost modeli 70,000 ta bemor ma'lumoti asosida muvaffaqiyatli o'qitildi.")
            return redirect('train_ai_model')

        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {e}")

    return render(request, 'ai_service/train_model.html', {'user_role': role})