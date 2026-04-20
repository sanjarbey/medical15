from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (visit_create_view,
PatientViewSet, VisitViewSet, 
patient_create_view, dashboard_view, 
LabResultViewSet, patient_list_view, patient_detail_view, 
patient_edit_view
)
# YANGI QATOR: AI view'sini chaqirib olamiz
from ai_service.views import train_ai_model_view
# API uchun yo'nalishlar
router = DefaultRouter()


router.register(r'patients', PatientViewSet)
router.register(r'visits', VisitViewSet)
router.register(r'lab-results', LabResultViewSet)


# YANGI QATOR: AI view'sini chaqirib olamiz
from ai_service.views import train_ai_model_view

urlpatterns = [
    # 1. Frontend (HTML interfeys) yo'nalishlari
    
    path('web/patients/', dashboard_view, name='dashboard'), # YANGI QATOR
    # YANGI: Bemorni ro'yxatga olish oynasi (Tashrifdan oldin turishi kerak!)
    path('web/patients/new/', patient_create_view, name='patient_create'),

    path('web/dashboard/', patient_list_view, name='patient_list'),
    path('web/patients/<int:pk>/', patient_detail_view, name='patient_detail'),

    # 2. API (JSON) yo'nalishlari (Orqa fonda qoladi)
    path('api/', include(router.urls)),

    # Frontend (HTML interfeys) yo'nalishlari
        
    # YANGI: Tashrif qo'shish oynasi
    path('web/visits/new/', visit_create_view, name='visit_create'),

    # SHU YERGA QO'SHING: AI Modelini o'qitish (Excel yuklash) sahifasi
    path('web/ai-training/', train_ai_model_view, name='train_ai_model'),

    path('web/patients/<int:pk>/edit/', patient_edit_view, name='patient_edit'),
]