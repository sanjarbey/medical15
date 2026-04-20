from rest_framework import serializers
from .models import Patient, Visit, LabResult, Symptom, VisitSymptom
from ai_service.models import AIRecommendation # YANGI: AI modelini chaqirib olamiz

# 1. AI xulosasi uchun serializator
class AIRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRecommendation
        fields = ['hypertension_risk', 'diabetes_risk', 'clinical_alert', 'calculated_at']

# 2. Laboratoriya tahlillari
class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = '__all__'

# 3. Tashrif simptomlari
class VisitSymptomSerializer(serializers.ModelSerializer):
    symptom_name = serializers.CharField(source='symptom.name_uz', read_only=True)
    
    class Meta:
        model = VisitSymptom
        fields = ['symptom', 'symptom_name', 'severity']

# 4. Tashriflar tarixi (Shu yerga AI ulanadi)
class VisitSerializer(serializers.ModelSerializer):
    lab_results = LabResultSerializer(many=True, read_only=True)
    visit_symptoms = VisitSymptomSerializer(source='visitsymptom_set', many=True, read_only=True)
    
    # YANGI: AI bashoratini tashrif ma'lumotlari ichiga qo'shib yuboramiz
    ai_prediction = AIRecommendationSerializer(read_only=True)

    class Meta:
        model = Visit
        fields = '__all__'

# 5. Bemor anketasi
class PatientSerializer(serializers.ModelSerializer):
    visits = VisitSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'patronymic', 'date_of_birth', 'created_at', 'visits']