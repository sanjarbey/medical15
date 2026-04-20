from django.db import models
from patients.models import Visit

class AIRecommendation(models.Model):
    # Bu xulosa qaysi tashrifga tegishli ekanligini bog'laymiz
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='ai_prediction', verbose_name="Tashrif")
    
    # Kasallik xavfi ehtimolliklari (foizda)
    hypertension_risk = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Gipertoniya xavfi (%)")
    diabetes_risk = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Diabet xavfi (%)")
    
    # Shifokor uchun tayyor matnli xulosa
    clinical_alert = models.TextField(verbose_name="Kognitiv tavsiya")
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Xulosasi: {self.visit.patient.first_name} ({self.calculated_at.strftime('%Y-%m-%d')})"
    

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)