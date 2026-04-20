import pandas as pd
import numpy as np

# 120,000 ta bemor qatori (Big Data)
n = 120000

print(f"⏳ {n} ta bemor ma'lumotlari shakllantirilmoqda. Iltimos kuting...")

# Tasodifiylikni qulflash (bir xil mantiq chiqishi uchun)
np.random.seed(42)

# Bemorlarning bo'yi (o'rtacha 165 sm) va vazni (o'rtacha 70 kg)
heights = np.random.normal(165, 10, n).astype(int)
weights = np.random.normal(70, 16, n).astype(int)

# TIBBIY MANTIQ 1: Qon bosimi vaznga qarab biroz ortadi
ap_hi = np.random.normal(115, 12, n) + (weights - 60) * 0.45
ap_hi = ap_hi.astype(int)

# Glukoza: 1 (Normal 75%), 2 (Yuqori 15%), 3 (Juda yuqori 10%)
gluc = np.random.choice([1, 2, 3], size=n, p=[0.75, 0.15, 0.10])

# TIBBIY MANTIQ 2: Yurak kasalligi ehtimoli (Qon bosimi > 135 yoki Vazn > 90 bo'lsa xavf yuqori)
cardio_prob = (ap_hi > 135).astype(float) * 0.6 + (weights > 90).astype(float) * 0.3
cardio_prob += np.random.uniform(0, 0.2, n) # Biologik farqlar uchun kichik tasodifiylik
cardio = (cardio_prob > 0.6).astype(int)

# Ma'lumotlarni jadvalga yig'ish (Sizning Django tizimingiz kutayotgan formatda)
df = pd.DataFrame({
    'id': range(1, n + 1),
    'height (cm)': heights,
    'weight': weights,
    'ap_hi': ap_hi,
    'gluc': gluc,
    'cardio': cardio
})

# Faylni .csv formatida saqlash (Sizning tizimingiz ";" ni o'qiydigan qilingan)
file_name = 'ai_his_bigdata_120k.csv'
df.to_csv(file_name, sep=';', index=False)

print(f"✅ MUVAFFAQIYATLI! '{file_name}' nomli fayl tayyor.")