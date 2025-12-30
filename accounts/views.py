from django.shortcuts import render
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response 
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model , authenticate
from .serializers import UserSerializers
from rest_framework.permissions import IsAuthenticated
from .validators import validate_password_strength
from .emailServices import EmailService, OTPService

User = get_user_model() # storing model to variable for easy access

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializers




# validate fields, generate otp and send it to user 

    @action(detail=False, methods=['post'])
    def signup(self, request):
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')

        # validate password
        try:
            validate_password_strength(password)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        return OTPService.generate_send_otp(email, first_name, last_name)



# verify the otp and save the user to database-----------------------------------------------------
    @action(detail=False, methods=['post'])
    def confirm_signup(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')

        otp, error_response = OTPService.verify_otp(email, otp_code)
        if error_response:
            return error_response
        
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

# Update password using old password ------------------------------------------------------------
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        user = request.user
        
        # validating all fields 
        if not current_password or not new_password or not confirm_password:
            return Response({"error": "Fill all fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        # checking new and confirm passwords if they are same
        if new_password != confirm_password:
            return Response({"error": "Passwords don't match"}, status=status.HTTP_400_BAD_REQUEST)
        
        # checking the current password if exist in the database
        if not user.check_password(current_password):
            return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        
        if current_password == new_password:  # Add this check
            return Response({"error": "New password must be different"}, status=status.HTTP_400_BAD_REQUEST)
        
        # validating password 
        try:
            validate_password_strength(new_password)
        except serializers.ValidationError as e:  # Add 'as e'
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Change password
        user.set_password(new_password)
        user.save()
        
        # Send notification (don't return it)
        EmailService.send_password_change_notification(user)
        
        # Return success response
        return Response({"message": "Password successfully updated"}, status=status.HTTP_200_OK)

# Update password using email OTP
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password_otp(self, request):
        user = request.user # current user
        email = request.user.email # current user's email
        
        try:
            return OTPService.generate_send_otp(email, user.first_name, user.last_name)
        except Exception as e:
            return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# confirm otp to change password
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def confirm_password_otp(self, request):
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        otp_code = request.data.get("otp_code")

        user = request.user #current user
        email = user.email # current user's email

        # checking for blank fields
        if not new_password or not confirm_password or not otp_code:
            return Response ({"error":"Fields are not filled"}, status=status.HTTP_400_BAD_REQUEST)
        
        # checking new and confirm passwords if they are same
        if new_password != confirm_password:
            return Response ({"error":"New password and confirm password are not same"}, status=status.HTTP_400_BAD_REQUEST)


        otp, error_response = OTPService.verify_otp(email, otp_code)
        if error_response:
           return error_response

        try:
            validate_password_strength(new_password)
        except serializers.ValidationError:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # saving otp as used 
        otp.is_used = True
        otp.save()
        # saving new password of user
        user.set_password(new_password)
        user.save()


        #change password
        
        EmailService.send_password_change_notification(user)
        return Response({"message": "Password successfully updated"}, status=status.HTTP_200_OK)

        

#logout user ----------------------------------------------------------------------------
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response ({'error':'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response ({'message':'logout successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response ({'error':f'{e}, token is not valid'}, status=status.HTTP_400_BAD_REQUEST)
        


# delete the user account -----------------------------------------------------------------------

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def delete_account(self, request):
        user = request.user
        try:
            user.delete()
            return Response ({'message':'User delete successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response ({'error':f'{e}, token is not valid'}, status=status.HTTP_400_BAD_REQUEST)


