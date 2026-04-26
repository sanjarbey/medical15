import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings

# Ogohlantirishlarni o'chirish (toza terminal uchun)
warnings.filterwarnings('ignore')

def train_and_save_models():
    file_name = 'ai_training_40k.csv'
    print(f"🔄 Ma'lumotlar {file_name} faylidan o'qilmoqda...")
    
    try:
        # Ma'lumotlarni o'qish (dataset generatorida sep=';' ishlatilgan)
        df = pd.read_csv(file_name, sep=';')
    except FileNotFoundError:
        print(f"❌ XATOLIK: {file_name} topilmadi. Avval generate_dataset.py ni ishga tushiring!")
        return

    # 1. Xususiyatlar (Features) va Maqsadli o'zgaruvchilarni (Targets) ajratish
    target_cols = ['target_htn', 'target_dm']
    X = df.drop(columns=target_cols)
    y_htn = df['target_htn']
    y_dm = df['target_dm']

    # Ustunlar ro'yxatini kelajakda (Django'da) ishlatish uchun saqlash
    feature_cols = X.columns.tolist()
    joblib.dump(feature_cols, 'feature_cols.pkl')
    print(f"✅ Ustunlar nomlari saqlandi: feature_cols.pkl ({len(feature_cols)} ta xususiyat)")

    # 2. Ma'lumotlarni O'qitish (80%) va Sinov (20%) qismlariga bo'lish
    X_train, X_test, y_htn_train, y_htn_test, y_dm_train, y_dm_test = train_test_split(
        X, y_htn, y_dm, test_size=0.2, random_state=42
    )

    # 3. XGBoost modellarini yaratish
    # (scale_pos_weight yoki boshqa murakkab sozlamalar hozircha shart emas, chunki data juda toza)
    model_htn = xgb.XGBClassifier(
        use_label_encoder=False, 
        eval_metric='logloss',
        random_state=42,
        learning_rate=0.1,
        max_depth=5,
        n_estimators=100
    )
    
    model_dm = xgb.XGBClassifier(
        use_label_encoder=False, 
        eval_metric='logloss',
        random_state=42,
        learning_rate=0.1,
        max_depth=5,
        n_estimators=100
    )

    # 4. Gipertoniya (HTN) modelini o'qitish va baholash
    print("\n🚀 Gipertoniya (HTN) modeli o'qitilmoqda...")
    model_htn.fit(X_train, y_htn_train)
    htn_preds = model_htn.predict(X_test)
    htn_acc = accuracy_score(y_htn_test, htn_preds)
    print(f"📊 HTN Modeli Aniqligi (Accuracy): {htn_acc * 100:.2f}%")
    print("HTN Hisoboti:\n", classification_report(y_htn_test, htn_preds))

    # 5. Qandli Diabet (DM) modelini o'qitish va baholash
    print("\n🚀 Qandli Diabet (DM) modeli o'qitilmoqda...")
    model_dm.fit(X_train, y_dm_train)
    dm_preds = model_dm.predict(X_test)
    dm_acc = accuracy_score(y_dm_test, dm_preds)
    print(f"📊 DM Modeli Aniqligi (Accuracy): {dm_acc * 100:.2f}%")
    print("DM Hisoboti:\n", classification_report(y_dm_test, dm_preds))

    # 6. Tayyor modellarni fayl ko'rinishida saqlash (Django ishlata olishi uchun)
    joblib.dump(model_htn, 'xgboost_htn_model.pkl')
    joblib.dump(model_dm, 'xgboost_dm_model.pkl')
    
    print("\n🎉 BARCHA JARAYONLAR MUVAFFAQIYATLI YAKUNLANDI!")
    print("Saqlangan fayllar:")
    print(" 1. feature_cols.pkl")
    print(" 2. xgboost_htn_model.pkl")
    print(" 3. xgboost_dm_model.pkl")
    print("Endi Django serverini (runserver) ishga tushirishingiz mumkin.")

if __name__ == "__main__":
    train_and_save_models()