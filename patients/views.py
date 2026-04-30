from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Case, When, Value, IntegerField, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.models import User
import json

# Loyiha modellari
from .models import Patient, Visit, LabResult, Symptom, VisitSymptom, PATIENT_SYMPTOM_IMPACT_CHOICES
from .serializers import PatientSerializer, VisitSerializer, LabResultSerializer
from ai_service.models import AIRecommendation 

# YANGI: AI servisini chaqirish
from ai_service.services import get_ai_prediction 

# Foydalanuvchi rolini aniqlab beruvchi yordamchi funksiya
def get_user_role(user):
    if user.is_superuser:
        return 'Super Admin'
    if user.groups.exists():
        return user.groups.first().name
    return 'Bemor'

# API ViewSets
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientSerializer

class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all().order_by('-visit_date')
    serializer_class = VisitSerializer

class LabResultViewSet(viewsets.ModelViewSet):
    queryset = LabResult.objects.all().order_by('-uploaded_at')
    serializer_class = LabResultSerializer

@login_required 
def patient_list_view(request):
    role = get_user_role(request.user)
    if role in ['Super Admin', 'Moderator', 'Shifokor', 'Hamshira']:
        patients = Patient.objects.all().order_by('-created_at')
    elif role == 'Bemor':
        patients = Patient.objects.filter(user=request.user)
    else:
        patients = Patient.objects.none()

    return render(request, 'patients/patient_list.html', {'patients': patients, 'user_role': role})

@login_required
def patient_detail_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    role = get_user_role(request.user)
    
    if role == 'Bemor' and patient.user != request.user:
        return HttpResponseForbidden("Siz boshqa bemorning kartasini ko'ra olmaysiz!")
        
    return render(request, 'patients/patient_detail.html', {'patient': patient, 'user_role': role})


@login_required
def visit_create_view(request):
    role = get_user_role(request.user)
    
    if role not in ['Super Admin', 'Shifokor', 'Hamshira']:
        return HttpResponseForbidden("Sizda yangi tashrif yaratish huquqi yo'q!")

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        patient = get_object_or_404(Patient, id=patient_id)
        
        assigned_doctor_id = request.POST.get('assigned_doctor')
        if assigned_doctor_id:
            assigned_doctor = User.objects.get(id=assigned_doctor_id)
        else:
            assigned_doctor = request.user 
        
        def clean_number(val, default_val=None):
            if not val:
                return default_val
            try:
                return float(str(val).replace(',', '.').strip())
            except ValueError:
                return default_val
        
        # 1. Tashrif ma'lumotlarini saqlash
        visit = Visit.objects.create(
            patient=patient,
            doctor=assigned_doctor,
            weight=clean_number(request.POST.get('weight')),
            height=clean_number(request.POST.get('height')),
            temperature=clean_number(request.POST.get('temperature'), 36.6),
            blood_pressure=request.POST.get('arterial_pressure') or request.POST.get('blood_pressure', '120/80'),
            heart_rate=clean_number(request.POST.get('heart_rate'), 75.0),
            doctor_notes=request.POST.get('doctor_notes', '')
        )
        
        # 2. Simptomlarni aylanib chiqib saqlash
        symptom_ids = request.POST.getlist('symptoms[]')
        severities = request.POST.getlist('severities[]')
        
        processed_symptoms = set() 
        last_symptom = None # AI ishga tushishi uchun bitta simptom obyekti kerak
        
        for s_id, sev in zip(symptom_ids, severities):
            if s_id and sev and s_id not in processed_symptoms:
                vs = VisitSymptom.objects.create(
                    visit=visit,
                    symptom_id=s_id,
                    severity=sev
                )
                last_symptom = vs # Oxirgi yaratilgan simptomni ushlab qolamiz
                processed_symptoms.add(s_id) 
                
        # ==========================================
        # 3. AI HISOBLASH (Barcha pichkalar bazaga tushgandan so'ng)
        # ==========================================
        if last_symptom:
            # AI endi bazadagi hamma belgilangan pichkalarni ko'ra oladi
            htn_prob, dm_prob = get_ai_prediction(last_symptom)
            
            # Natijani shu tashrifdagi barcha simptom qatorlariga yozib qo'yamiz
            VisitSymptom.objects.filter(visit=visit).update(
                htn_risk=htn_prob,
                dm_risk=dm_prob
            )
        # ==========================================

        # 4. Laboratoriya fayllarini saqlash
        lab_types = request.POST.getlist('lab_types[]')
        lab_files = request.FILES.getlist('lab_files[]') 

        if lab_files:
            for test_type, uploaded_file in zip(lab_types, lab_files):
                if uploaded_file:
                    LabResult.objects.create(
                        visit=visit,
                        test_type=test_type, 
                        file=uploaded_file 
                    )
            
        return redirect('patient_detail', pk=patient.id)

    # GET so'rovi (sahifa yangi ochilganda)
    patients = Patient.objects.all().order_by('last_name')
    symptoms = Symptom.objects.all().order_by('name_uz')
    doctors = User.objects.filter(groups__name='Shifokor')
    
    return render(request, 'patients/visit_create.html', {
        'patients': patients,
        'symptoms': symptoms,
        'severities': PATIENT_SYMPTOM_IMPACT_CHOICES,
        'doctors': doctors,
        'user_role': role
    })


@login_required
def dashboard_view(request):
    role = get_user_role(request.user)
    
    if role == 'Bemor':
        try:
            patient = Patient.objects.get(user=request.user)
            recent_visits = Visit.objects.filter(patient=patient).order_by('-visit_date')[:5]
            
            latest_ai_alert = None
            latest_htn_risk = 0
            latest_dm_risk = 0
            
            if recent_visits.exists():
                ai_rec = AIRecommendation.objects.filter(visit=recent_visits.first()).first()
                if ai_rec:
                    latest_ai_alert = ai_rec.clinical_alert
                    latest_htn_risk = ai_rec.hypertension_risk
                    latest_dm_risk = ai_rec.diabetes_risk

            context = {
                'is_patient': True,
                'patient': patient,
                'total_personal_visits': Visit.objects.filter(patient=patient).count(),
                'latest_ai_alert': latest_ai_alert,
                'latest_htn_risk': latest_htn_risk,
                'latest_dm_risk': latest_dm_risk,
                'recent_visits': recent_visits
            }
            return render(request, 'patients/dashboard.html', context)
        except Patient.DoesNotExist:
            return render(request, 'patients/dashboard.html', {'is_patient': True, 'error': "Anketa topilmadi."})

    if role in ['Super Admin', 'Moderator']:
        my_visits = Visit.objects.all()
        table_visits = Visit.objects.all().order_by('-visit_date')
        total_patients = Patient.objects.count()
        dashboard_title = "Boshqaruv Analitikasi (Umumiy)"
    elif role in ['Shifokor', 'Hamshira']:
        my_visits = Visit.objects.filter(doctor=request.user)
        total_patients = Patient.objects.filter(id__in=my_visits.values_list('patient_id', flat=True)).count()
        dashboard_title = f"Analitika va Bemorlar ({role})"
        
        table_visits = Visit.objects.annotate(
            is_mine=Case(
                When(doctor=request.user, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('-is_mine', '-visit_date')
    else:
        return HttpResponseForbidden("Xatolik! Kirish huquqi yo'q.")

    total_visits = my_visits.count()
    high_risk_htn = AIRecommendation.objects.filter(visit__in=my_visits, hypertension_risk__gt=60).count()
    high_risk_dm = AIRecommendation.objects.filter(visit__in=my_visits, diabetes_risk__gt=60).count()

    htn_percent = round((high_risk_htn / total_visits * 100), 1) if total_visits > 0 else 0
    dm_percent = round((high_risk_dm / total_visits * 100), 1) if total_visits > 0 else 0

    critical_cases = AIRecommendation.objects.filter(
        Q(hypertension_risk__gt=60) | Q(diabetes_risk__gt=60),
        visit__in=my_visits
    ).order_by('-calculated_at')[:5]

    context = {
        'is_patient': False,
        'dashboard_title': dashboard_title,
        'total_patients': total_patients,
        'total_visits': total_visits,
        'high_risk_htn': high_risk_htn,
        'high_risk_dm': high_risk_dm,
        'htn_percent': htn_percent,
        'dm_percent': dm_percent,
        'critical_cases': critical_cases,
        'table_visits': table_visits,
    }
    return render(request, 'patients/dashboard.html', context)


@login_required
def patient_create_view(request):
    role = get_user_role(request.user)
    
    if role not in ['Super Admin', 'Moderator', 'Shifokor', 'Hamshira']:
        return HttpResponseForbidden("Xatolik! Sizda yangi bemor ro'yxatga olish huquqi yo'q.")

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        patronymic = request.POST.get('patronymic')
        date_of_birth = request.POST.get('date_of_birth')
        gender_val = request.POST.get('gender', 'Erkak')

        Patient.objects.create(
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            date_of_birth=date_of_birth,
            gender=gender_val 
        )
        return redirect('patient_list')

    return render(request, 'patients/patient_create.html', {'user_role': role})


@login_required
def patient_edit_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        patient.first_name = request.POST.get('first_name')
        patient.last_name = request.POST.get('last_name')
        patient.patronymic = request.POST.get('patronymic', '')
        patient.date_of_birth = request.POST.get('date_of_birth')
        patient.gender = request.POST.get('gender')
        
        patient.save() 
        return redirect('patient_detail', pk=patient.id)

    return render(request, 'patients/patient_edit.html', {'patient': patient})


def save_ai_feedback(request, symptom_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            feedback_value = data.get('feedback')
            
            symptom = VisitSymptom.objects.get(id=symptom_id)
            symptom.doctor_feedback = feedback_value
            symptom.save(update_fields=['doctor_feedback'])
            
            return JsonResponse({"status": "success", "message": "Bahoyingiz saqlandi!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "invalid_method"}, status=405)