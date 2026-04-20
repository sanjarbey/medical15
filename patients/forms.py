from django import forms
from .models import Visit, Symptom

class VisitForm(forms.ModelForm):
    # Simptomlarni checkbox ko'rinishida chiqarish
    symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'symptom-checkbox'}),
        required=False,
        label="Bemor simptomlari"
    )

    class Meta:
        model = Visit
        fields = ['patient', 'weight', 'blood_pressure', 'symptoms'] # o'zingizdagi maydonlar