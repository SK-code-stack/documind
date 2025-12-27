from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializers
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP
User = get_user_model() # storing model to variable for easy access

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializers


    @action(detail=False, methods='post')
    def send_otp(self, request):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            email = serializer.validate_data['email']

            #delete old otp for this email
            OTP.objects.filter(email=email).delete()

            #generate new otp
            otp_code = OTP.generate_otp()
            OTP.objects.create(email = email, otp = otp_code)

            #send otp through email
            send_mail(
                'DocuMind OTP ', 
                f'Your OTP is {otp_code}. Valid for 10 minutes',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )

            return Response({'message':'OTP send successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# signup user 

    @action(detail=False, methods=['post'])
    def signup(self, request):
        email = request.data.get('email')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete old OTPs
        OTP.objects.filter(email=email).delete()
        
        # Generate and send OTP
        otp_code = OTP.generate_otp(self)
        OTP.objects.create(email=email, otp=otp_code)
        
        try:
            send_mail(
                'Your OTP Code',
                f'Your OTP is: {otp_code}. Valid for 10 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Store user data temporarily (don't create user yet)
        return Response({
            'message': 'OTP sent to your email. Please verify to complete signup.',
            'email': email
        }, status=status.HTTP_200_OK)




# we have to rewrite this api write 2 api one to send otp to email by name second for signup