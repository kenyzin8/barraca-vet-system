# serializers.py
from rest_framework import serializers

class ConsultationSerializer(serializers.Serializer):
    selectedPetId = serializers.IntegerField()
    appointment_date = serializers.DateField(input_formats=['%b %d, %Y'], required=False)
    appointment_time_of_the_day = serializers.CharField(required=False)
    lab_results = serializers.CharField()
    temperature = serializers.FloatField()
    weight = serializers.FloatField()
    diagnosis = serializers.CharField()
    treatment = serializers.CharField()
    med_images = serializers.ImageField(required=False)
    isDeworming = serializers.BooleanField()
    isVaccination = serializers.BooleanField()
    productsSelected = serializers.JSONField(required=False)
    appointment_purpose = serializers.IntegerField(required=False)
