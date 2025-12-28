from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response 
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model , authenticate
from .serializers import UserSerializers
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP
from django.http import HttpResponse
User = get_user_model() # storing model to variable for easy access

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializers




# validate fields, generate otp and send it to user 

    @action(detail=False, methods=['post'])
    def signup(self, request):
        email = request.data.get('email')
        fname = request.data.get('first_name')
        
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
                f'Welcome to DocuMind {fname}',
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

    # verify the otp and save the user to database-----------------------------------------------------
    @action(detail=False, methods=['post'])
    def confirm_signup(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')

        try:
            otp = OTP.objects.get(email=email, otp = otp_code)
            if not otp.is_valid():
                return Response({'error':'OTP is already used'}, status=status.HTTP_400_BAD_REQUEST)
        except otp.DoesNotExist:
            return Response({'error':'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        #mark otp as used
        otp.is_used = True
        otp.save()
        #create user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_verified = True
            user.save()

            #delete otp after user signup
            otp.delete()

            #generate token for this user
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh':str(refresh),
                'access':str(refresh.access_token),
                'user':UserSerializers(user).data,
            },status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# login user -----------------------------------------------------

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=email, password=password)

        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh":str(refresh),
            "access":str(refresh.access_token),
            "user":{
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            } ,
        }, status=status.HTTP_200_OK)







