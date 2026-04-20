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

# 3. Jadvallarni tizimga kiritish
admin.site.register(Patient)
admin.site.register(Visit, VisitAdmin)
admin.site.register(LabResult)
admin.site.register(Symptom, SymptomAdmin)