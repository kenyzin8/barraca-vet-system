# serializers.py
from rest_framework import serializers
from .models import TemporaryLabResultImage
import json

class TemporaryLabResultImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemporaryLabResultImage
        fields = ('image',)

class ConsultationSerializer(serializers.Serializer):
    selectedPetId = serializers.IntegerField()
    appointment_date = serializers.DateField(input_formats=['%b %d, %Y'], required=False)
    appointment_time_of_the_day = serializers.CharField(required=False)
    symptoms = serializers.CharField()
    temperature = serializers.FloatField()
    weight = serializers.FloatField()
    diagnosis = serializers.CharField()
    treatment = serializers.CharField()
    labResultsDescriptions = serializers.JSONField(required=True)
    labResultsImageIDS = serializers.JSONField(required=False)
    isDeworming = serializers.BooleanField()
    isVaccination = serializers.BooleanField()
    productsSelected = serializers.JSONField(required=False)
    appointment_purpose = serializers.IntegerField(required=False)

class PrescriptionSerializer(serializers.Serializer):
    selectedPetId = serializers.IntegerField(required=True)
    productsSelected = serializers.JSONField(required=True)

class HealthCardSerializer(serializers.Serializer):
    selectedPetId = serializers.IntegerField()
    productSelected = serializers.IntegerField(required=True)
    medicine_sticker = serializers.ImageField(required=False)

    temperature = serializers.FloatField()
    weight = serializers.FloatField()
    treatment = serializers.CharField()
    isDeworming = serializers.BooleanField()
    isVaccination = serializers.BooleanField()
    
    appointment_date = serializers.DateField(input_formats=['%b %d, %Y'], required=False)
    appointment_time_of_the_day = serializers.CharField(required=False)
    appointment_purpose = serializers.IntegerField(required=False)

    custom_purpose = serializers.CharField(required=False)