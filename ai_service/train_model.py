import pandas as pd
import xgboost as xgb
import joblib
import os
def train_and_save_models():
    # 1. Datasetni yuklash
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../ai_training_100k.csv'), sep=';')
    
    # QATORLARNI RAQAMGA O'TKAZISH (MUHIM!)
    numeric_cols = ['weight', 'height', 'temperature', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'age']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # Agar noto'g'ri qiymatlar (NaN) bo'lsa, ularni 0 bilan to'ldiramiz
    df = df.fillna(0)

    # 2. Xususiyatlar (Features) va Maqsad (Target)
    X = df.drop(columns=['has_htn', 'has_dm'])
    y_htn = df['has_htn']
    y_dm = df['has_dm']
    
    # Tartibni saqlash (Keyinchalik services.py da kerak bo'ladi)
    joblib.dump(list(X.columns), 'feature_cols.pkl')
    
    # 3. Modellarni o‘qitish
    model_htn = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model_htn.fit(X, y_htn)
    
    model_dm = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model_dm.fit(X, y_dm)
    
    # 4. Saqlash
    joblib.dump(model_htn, 'xgboost_htn_model.pkl')
    joblib.dump(model_dm, 'xgboost_dm_model.pkl')
    print("Modellar muvaffaqiyatli o‘qitildi va saqlandi!")

if __name__ == "__main__":
    train_and_save_models()
   