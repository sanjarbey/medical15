from django.contrib import admin
from .models import Patient, Visit, LabResult, Symptom, VisitSymptom

# 1. Avval Inline klassi yozilishi shart (Python shuni o'qib oladi)
class VisitSymptomInline(admin.TabularInline):
    model = VisitSymptom
    extra = 1 

# 2. Keyin esa uni o'z ichiga oluvchi Asosiy klass yoziladi
class VisitAdmin(admin.ModelAdmin):
    inlines = [VisitSymptomInline] # Mana bu yerda xatosiz topiladi
    exclude = ('symptoms',)
    readonly_fields = ('bmi',) 

# Simptomlar jadvalini qulay ko'rish uchun (oldingi qadamda qo'shgan edik)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'code_name', 'weight_htn', 'weight_dm')
    search_fields = ('name_uz', 'code_name')


# === VisitSymptom ni Admin panelga qo'shish ===
@admin.register(VisitSymptom)
class VisitSymptomAdmin(admin.ModelAdmin):
    # Admin panel ro'yxatida qaysi ustunlar ko'rinishini belgilash
    list_display = ('id', 'get_patient_name', 'blood_pressure', 'htn_risk', 'dm_risk')
    
    # Qidiruv tizimini qo'shish (Bemor ism-familiyasi bo'yicha)
    search_fields = ('visit__patient__first_name', 'visit__patient__last_name', 'blood_pressure')
    
    # O'ng tomonda filtr qo'shish (Masalan, xavf darajasi bo'yicha)
    list_filter = ('htn_risk', 'dm_risk')

    # Bemor ismini chiqarib beruvchi yordamchi funksiya
    def get_patient_name(self, obj):
        return f"{obj.visit.patient.first_name} {obj.visit.patient.last_name}"
    get_patient_name.short_description = 'Bemor'


# 3. Jadvallarni tizimga kiritish
admin.site.register(Patient)
admin.site.register(Visit, VisitAdmin)
admin.site.register(LabResult)
admin.site.register(Symptom, SymptomAdmin)