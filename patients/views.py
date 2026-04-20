from django.contrib.auth.decorators import login_required # YANGI MODUL
from rest_framework import viewsets
from .models import Patient, Visit, LabResult
from .serializers import PatientSerializer, VisitSerializer, LabResultSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import  Symptom, VisitSymptom, LabResult, PATIENT_SYMPTOM_IMPACT_CHOICES
from django.db.models import Count,Case, When, Value, IntegerField, Q
from ai_service.models import AIRecommendation # AI bazasini chaqirib olamiz
from django.http import HttpResponseForbidden # YANGI
from django.contrib.auth.models import User # Eng tepaga qo'shib qo'ying (agar yo'q bo'lsa)
# Foydalanuvchi rolini aniqlab beruvchi yordamchi funksiya
def get_user_role(user):
    if user.is_superuser:
        return 'Super Admin'
    if user.groups.exists():
        return user.groups.first().name
    return 'Bemor' # Guruhlanmaganlar avtomat bemor hisoblanadi


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
    
    # Shifokor, Hamshira va Moderatorlar BARCHA bemorlarni ko'radi
    if role in ['Super Admin', 'Moderator', 'Shifokor', 'Hamshira']:
        patients = Patient.objects.all().order_by('-created_at')
    # Bemor esa FAQAT O'ZINI ko'radi
    elif role == 'Bemor':
        patients = Patient.objects.filter(user=request.user)
    else:
        patients = Patient.objects.none()

    return render(request, 'patients/patient_list.html', {'patients': patients, 'user_role': role})

@login_required
def patient_detail_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    role = get_user_role(request.user)
    
    # Bemor birovning kartasiga kirishiga yo'l qo'ymaslik xavfsizligi
    if role == 'Bemor' and patient.user != request.user:
        return HttpResponseForbidden("Siz boshqa bemorning kartasini ko'ra olmaysiz!")
        
    return render(request, 'patients/patient_detail.html', {'patient': patient, 'user_role': role})

@login_required
def visit_create_view(request):
    role = get_user_role(request.user)
    
    # Yangi tashrifni faqat Shifokor va Hamshira qo'sha oladi (Bemor yoki Moderator emas)
    if role not in ['Super Admin', 'Shifokor', 'Hamshira']:
        return HttpResponseForbidden("Sizda yangi tashrif yaratish huquqi yo'q!")
    
@login_required
def visit_create_view(request):
    role = get_user_role(request.user)
    
    # Yangi tashrifni faqat Shifokor va Hamshira qo'sha oladi
    if role not in ['Super Admin', 'Shifokor', 'Hamshira']:
        return HttpResponseForbidden("Sizda yangi tashrif yaratish huquqi yo'q!")

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        patient = get_object_or_404(Patient, id=patient_id)
        
        # YANGI QISM: Formadan hamshira tanlagan shifokorni qabul qilamiz
        assigned_doctor_id = request.POST.get('assigned_doctor')
        if assigned_doctor_id:
            assigned_doctor = User.objects.get(id=assigned_doctor_id)
        else:
            assigned_doctor = request.user # Agar hech kim tanlanmasa, o'ziga yoziladi
        
        # ==========================================
        # YANGI QO'SHILGAN QISM: Raqamlarni tozalash (Sanitization)
        # ==========================================
        def clean_number(val, default_val=None):
            if not val:
                return default_val
            try:
                # Agar foydalanuvchi vergul kiritgan bo'lsa ham, nuqtaga o'zgartiramiz
                return float(str(val).replace(',', '.').strip())
            except ValueError:
                return default_val
        # ==========================================
        
        # 1. Tashrif ma'lumotlarini saqlash
        visit = Visit.objects.create(
            patient=patient,
            doctor=assigned_doctor,
            weight=clean_number(request.POST.get('weight')),
            height=clean_number(request.POST.get('height')),
            temperature=clean_number(request.POST.get('temperature'), 36.6),
            blood_pressure=request.POST.get('arterial_pressure') or request.POST.get('blood_pressure', '120/80'), # <--- YANGI QATOR
            heart_rate=clean_number(request.POST.get('heart_rate'), 75.0),
            doctor_notes=request.POST.get('doctor_notes', '')
        )
        
        # 2. Simptomlar va ularning darajalarini saqlash
        symptom_ids = request.POST.getlist('symptoms[]')
        severities = request.POST.getlist('severities[]')
        
        processed_symptoms = set() 
        for s_id, sev in zip(symptom_ids, severities):
            if s_id and sev and s_id not in processed_symptoms:
                VisitSymptom.objects.create(
                    visit=visit,
                    symptom_id=s_id,
                    severity=sev
                )
                processed_symptoms.add(s_id) 
                
        # ==========================================
        # 3. Bir nechta Laboratoriya fayllarini saqlash
        # ==========================================
        # Formadan ro'yxat (list) ko'rinishida kelayotgan tahlil turlari va fayllarni ushlab olamiz
        lab_types = request.POST.getlist('lab_types[]')
        lab_files = request.FILES.getlist('lab_files[]') 

        # Agar hech bo'lmaganda 1 ta fayl yuklangan bo'lsa
        if lab_files:
            # Fayllar va ularning turlarini juftlashtirib (zip) aylanib chiqamiz
            for test_type, uploaded_file in zip(lab_types, lab_files):
                # Bo'sh qatorlar saqlanib qolmasligi uchun tekshiramiz
                if uploaded_file:
                    LabResult.objects.create(
                        visit=visit,
                        test_type=test_type,  # Masalan: 'qon', 'rentgen'
                        file=uploaded_file    # Yuklangan PDF yoki rasm fayli
                    )
        # ==========================================
            
        return redirect('patient_detail', pk=patient.id)

    # GET so'rovi (sahifa yangi ochilganda)
    patients = Patient.objects.all().order_by('last_name')
    symptoms = Symptom.objects.all().order_by('name_uz')
    # print(symptoms)
    # YANGI QISM: Faqatgina 'Shifokor' guruhidagi foydalanuvchilarni bazadan qidirib topish
    doctors = User.objects.filter(groups__name='Shifokor')
    
    return render(request, 'patients/visit_create.html', {
        'patients': patients,
        'symptoms': symptoms,
        'severities': PATIENT_SYMPTOM_IMPACT_CHOICES,
        'doctors': doctors, # Shifokorlar ro'yxatini HTML ga uzatamiz
        'user_role': role
    })
# patients/views.py faylidagi o'zgarishlar

@login_required
def dashboard_view(request):
    role = get_user_role(request.user)
    # ==========================================
    # 1. BEMOR UCHUN (Shaxsiy salomatlik)
    # ==========================================
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
            return render(request, 'patients/dashboard.html', 
                          {
                              'is_patient': True, 
                              'error': "Anketa topilmadi."
                           }
                          )
        pass

    # ==========================================
    # 2. XODIMLAR VA BOSHQARUVCHILAR UCHUN
    # ==========================================
    
    # A) Super Admin va Moderator hamma narsani ko'radi
    if role in ['Super Admin', 'Moderator']:
        my_visits = Visit.objects.all()
        table_visits = Visit.objects.all().order_by('-visit_date')
        total_patients = Patient.objects.count()
        dashboard_title = "Boshqaruv Analitikasi (Umumiy)"
        # critical_count = sum(1 for v in my_visits if v.htn_risk > 80 or v.dm_risk > 80)
    elif role in ['Shifokor', 'Hamshira']:
        # Statistika uchun faqat o'zi ko'rgan bemorlar
        my_visits = Visit.objects.filter(doctor=request.user)
        total_patients = Patient.objects.filter(id__in=my_visits.values_list('patient_id', flat=True)).count()
        dashboard_title = f"Analitika va Bemorlar ({role})"
        
        # JADVAL UCHUN: O'zining bemorlari eng tepada (is_mine=1), keyin boshqalar (is_mine=0), keyin sana bo'yicha
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
        'table_visits': table_visits, # YANGI: Jadval uchun maxsus saralangan ro'yxat
        # 'critical_count': critical_count
    }
    return render(request, 'patients/dashboard.html', context)

@login_required
def patient_create_view(request):
    role = get_user_role(request.user)
    
    # YANGI XAVFSIZLIK QULFI: Yangi bemorni faqat shu 4 ta rol vakillari qo'sha oladi
    if role not in ['Super Admin', 'Moderator', 'Shifokor', 'Hamshira']:
        return HttpResponseForbidden("Xatolik! Sizda yangi bemor ro'yxatga olish huquqi yo'q.")

    if request.method == 'POST':
        # Formadan kelgan ma'lumotlarni o'qib olish
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        patronymic = request.POST.get('patronymic')
        date_of_birth = request.POST.get('date_of_birth')
        gender_val = request.POST.get('gender', 'Erkak') # Yangi qo'shilgan qator

        # Bazada yangi Bemor yaratish
        new_patient = Patient.objects.create(
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            date_of_birth=date_of_birth,
            gender=gender_val  # <--- Shu qatorni qo'shish esdan chiqmasin
        )
        
        # Bemor yaratilgach, uning shaxsiy kartasiga yo'naltirish
        return redirect('patient_list')

    # GET so'rovi uchun (sahifa birinchi marta ochilganda)
    return render(request, 'patients/patient_create.html', {'user_role': role})


@login_required
def patient_edit_view(request, pk):
    # 1. Tahrirlanmoqchi bo'lgan bemorni topib kelamiz
    patient = get_object_or_404(Patient, pk=pk)

    # 2. Agar shifokor formani o'zgartirib "Saqlash" tugmasini bossa
    if request.method == 'POST':
        patient.first_name = request.POST.get('first_name')
        patient.last_name = request.POST.get('last_name')
        patient.patronymic = request.POST.get('patronymic', '')
        patient.date_of_birth = request.POST.get('date_of_birth')
        patient.gender = request.POST.get('gender')
        
        patient.save() # Yangi ma'lumotlarni bazaga yozamiz
        
        # Tahrirlab bo'lgach, bemorning shaxsiy profiliga qaytaramiz
        return redirect('patient_detail', pk=patient.id)

    # 3. Agar shunchaki sahifaga kirsa, eski ma'lumotlari bilan formani ochib beramiz
    context = {
        'patient': patient
    }
    return render(request, 'patients/patient_edit.html', context)