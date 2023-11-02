from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from record_management.models import Pet

from .serializers import PetSerializer, UserLoginSerializer

class PetAPIView(APIView):
    throttle_scope = 'get_pet'

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pet_id = request.GET.get('pet_id')
        
        if not pet_id:
            return Response({"error": "Missing 'pet_id'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pet = Pet.objects.get(id=pet_id)
            serializer = PetSerializer(pet)
            return Response(serializer.data)
        except Pet.DoesNotExist:
            return Response({"error": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

class APILoginView(APIView):
    throttle_scope = 'mobile_login'

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
        