from django.db.models.signals import post_save
from django.dispatch import receiver
from patients.models import VisitSymptom
from .services import get_ai_prediction

@receiver(post_save, sender=VisitSymptom)
def trigger_ai_from_symptoms(sender, instance, created, **kwargs):
    """
    VisitSymptom bazaga yozilganda AI ni avtomatik ishga tushiradi.
    """
    # 1. Bashoratni olish
    htn_prob, dm_prob = get_ai_prediction(instance)
    
    # 2. Bazani update orqali yangilash (post_save ni qayta chaqirmaydi!)
    VisitSymptom.objects.filter(pk=instance.pk).update(
        htn_risk=htn_prob,
        dm_risk=dm_prob
    )