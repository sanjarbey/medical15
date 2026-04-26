from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LabResult
from .ocr_service import extract_data_from_pdf



@receiver(post_save, sender=LabResult)
def process_lab_pdf(sender, instance, created, **kwargs):
    if created and instance.file:
        data = extract_data_from_pdf(instance.file.path)
        
        # Yangilangan ustunlarga ma'lumotlarni saqlash
        LabResult.objects.filter(id=instance.id).update(
            extracted_text=data['text'],
            hemoglobin=data['hb'],
            erythrocytes=data['rbc'],
            leukocytes=data['wbc'],
            platelets=data['plt']
        )