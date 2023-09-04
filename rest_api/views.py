from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from record_management.models import Pet
from .serializers import PetSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class TokenGenerator(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        admin_username = request.data.get('admin_username')
        admin_password = request.data.get('admin_password')

        user_id = request.data.get('user_id')

        admin_user = authenticate(username=admin_username, password=admin_password)

        if admin_user is not None and admin_user.is_staff:
            try:
                user = User.objects.get(id=user_id)
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key})
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid admin credentials"}, status=status.HTTP_403_FORBIDDEN)

    def get(self, request):
        admin_username = request.GET.get('admin_username')
        admin_password = request.GET.get('admin_password')
        user_id = request.GET.get('user_id')

        # get token of user_id
        admin_user = authenticate(username=admin_username, password=admin_password)
        if admin_user is not None and admin_user.is_staff:
            try:
                user = User.objects.get(id=user_id)
                token = Token.objects.get(user=user)
                return Response({"token": token.key})
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            except Token.DoesNotExist:
                return Response({"error": "Token not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid admin credentials"}, status=status.HTTP_403_FORBIDDEN)


class PetAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pet_id = request.GET.get('pet_id')
        
        if not pet_id:
            return Response({"error": "Missing 'pet_id'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pet = Pet.objects.get(id=pet_id)
            serializer = PetSerializer(pet)
            print("Rest API Called for Pet ID: ", pet_id)
            return Response(serializer.data)
        except Pet.DoesNotExist:
            return Response({"error": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)
