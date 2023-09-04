from rest_framework import serializers
from record_management.models import Pet

from rest_framework import serializers
from django.contrib.auth import authenticate

from django.utils import timezone

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if user:
                user.last_login = timezone.now()
                user.save()
                return {"status": True}
            else:
                raise serializers.ValidationError({"status": False})
        else:
            raise serializers.ValidationError({"status": False})

        return data

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = '__all__' 