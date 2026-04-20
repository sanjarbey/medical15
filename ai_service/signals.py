from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from patients.models import VisitSymptom, LabResult
from .services import get_ai_prediction
from ai_service.models import Patient
# Simptomlar o'zgarganda AI ni ishga tushirish
@receiver(post_save, sender=VisitSymptom)
@receiver(post_delete, sender=VisitSymptom)
def trigger_ai_from_symptoms(sender, instance, **kwargs):
    htn_prob, dm_prob = get_ai_prediction(instance)
    instance.htn_risk = htn_prob
    instance.dm_risk = dm_prob
    instance.save()

# YANGI: Laboratoriya natijasi (PDF) yuklanganda AI ni ishga tushirish
@receiver(post_save, sender=LabResult)
def trigger_ai_from_lab(sender, instance, **kwargs):
    if instance.visit:
        calculate_disease_risk(instance.visit)