from django.db import models
from django.contrib.auth.models import User # YANGI QATOR
# 1. BEMORLAR JADVALI
class Patient(models.Model):
    GENDER_CHOICES = (
        ('Erkak', 'Erkak'),
        ('Ayol', 'Ayol'),
    )
    # YANGI QATOR: Bemorning tizimga kirish logini bilan bog'lash
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tizimga kirish akkaunti")
    first_name = models.CharField(max_length=50, verbose_name="Ismi")
    last_name = models.CharField(max_length=50, verbose_name="Familiyasi")
    patronymic = models.CharField(max_length=50, blank=True, null=True, verbose_name="Otasining ismi")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Erkak', verbose_name="Jinsi")
    date_of_birth = models.DateField(verbose_name="Tug'ilgan sanasi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# 2. SIMPTOMLAR JADVALI (AI tushunishi uchun bazaviy ro'yxat)
class Symptom(models.Model):
    name_uz = models.CharField(max_length=100, verbose_name="Simptom nomi (O'zbekcha)")
    code_name = models.CharField(max_length=50, unique=True, verbose_name="Tibbiy kodi (AI uchun)")
    
    # YANGI: Kasalliklar bo'yicha simptomning vazni (-1.00 dan 1.00 gacha)
    weight_htn = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="HTN (Gipertoniya) vazni")
    weight_dm = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="DM (Diabet) vazni")

    def __str__(self):
        return self.name_uz

# 3. TASHRIF VA SIMPTOM ORALIQ JADVALI (Simptom darajasini belgilash uchun)
SEVERITY_CHOICES = (
    (1, 'Yengil (Kuchsiz)'),
    (2, 'O\'rtacha'),
    (3, 'Og\'ir (Kuchli)'),
)

# 1. 9 ta darajali V1-V9 shkalasini shu yerga ko'chiramiz
PATIENT_SYMPTOM_IMPACT_CHOICES = (
    (0.00,  'Taʼsir yo‘q '),
    (0.25,  'Taʼsir kuchsiz '),
    (0.50,  'O‘rtacha taʼsir '),
    (0.75,  'Taʼsiri kuchli '),
    (1.00,  'Taʼsiri juda kuchli'),
)

class VisitSymptom(models.Model):
    visit = models.ForeignKey('Visit', on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE, verbose_name="Simptom")
    # O'ZGARISH: Terapevt endi bemor holatiga qarab V1-V9 darajalaridan birini tanlaydi
    severity = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        choices=PATIENT_SYMPTOM_IMPACT_CHOICES, 
        default=0.50, 
        verbose_name="Bemordagi darajasi"
    )

    class Meta:
        unique_together = ('visit', 'symptom') 

    def __str__(self):
        return f"{self.symptom.name_uz} - {self.get_severity_display()}"

# 4. TASHRIFLAR JADVALI
class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits', verbose_name="Bemor")
    visit_date = models.DateTimeField(auto_now_add=True, verbose_name="Qabul vaqti")
    # YANGI QATOR: Tashrifni yaratgan (qabul qilgan) shifokor yoki hamshirani saqlash
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Qabul qilgan xodim")
    
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Vazni (kg)")
    height = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Bo'yi (sm)")
    bmi = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Tana massasi indeksi (BMI)")
    
    temperature = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Tana harorati")
    blood_pressure = models.CharField(max_length=20, default="120/80", verbose_name="Qon bosimi", null=True, blank=True)
    # arterial_pressure = models.CharField(max_length=15, verbose_name="Arterial qon bosimi")
    # venous_pressure = models.CharField(max_length=15, blank=True, null=True, verbose_name="Vena qon bosimi")
    heart_rate = models.IntegerField(verbose_name="Yurak urishi")
    
    symptoms = models.ManyToManyField(Symptom, through='VisitSymptom', related_name='visits', verbose_name="Simptomlar")
    doctor_notes = models.TextField(blank=True, null=True, verbose_name="Shifokor xulosasi / Qo'shimcha izoh")

    def save(self, *args, **kwargs):
        # BMI avtomatik hisoblash mantig'i
        if self.weight and self.height:
            height_in_meters = float(self.height) / 100.0
            calculated_bmi = float(self.weight) / (height_in_meters ** 2)
            self.bmi = round(calculated_bmi, 2)
        super(Visit, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.first_name} - {self.visit_date.strftime('%Y-%m-%d')}"

# 5. LABORATORIYA TAHLILLARI JADVALI
TEST_TYPE_CHOICES = (
    ('qon', 'Qon tahlili'),
    ('peshob', 'Peshob (Siydik) tahlili'),
    ('rentgen', 'Rentgen / MRT xulosasi'),
    ('boshqa', 'Boshqa tahlillar'),
)

class LabResult(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='lab_results', verbose_name="Tashrif")
    test_type = models.CharField(max_length=50, choices=TEST_TYPE_CHOICES, verbose_name="Tahlil turi")
    file = models.FileField(upload_to='lab_results_pdfs/', verbose_name="PDF fayl yuklash")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # NLP orqali o'qib olinadigan matn
    extracted_text = models.TextField(blank=True, null=True, verbose_name="O'qib olingan to'liq matn")
    
    # PDF dan ajratib olinadigan aniq ko'rsatkichlar
    hemoglobin = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Gemoglobin (HB)")
    erythrocytes = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Eritrotsitlar (RBC)")
    leukocytes = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Leykotsitlar (WBC)")
    platelets = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Trombotsitlar (PLT)")
    
    def __str__(self):
        return f"{self.get_test_type_display()} ({self.visit.patient.first_name})"