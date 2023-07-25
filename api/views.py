import json

from django.http import JsonResponse
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from .jwt_utils import generate_token, verify_token
from .models import TwoFactorAuth


@csrf_exempt
def login(request):
    if request.method == 'POST':
        raw_data = request.body.decode('utf-8')
        # Parse the JSON data
        data = json.loads(raw_data or '{}')

        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username)
            # Check the password using Django's check_password
            if check_password(password, user.password):
                # Create a JWT token with user ID as payload
                token = generate_token({'user_id': user.id})
                return JsonResponse({'token': token})
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def token_refresh(request):
    if request.method == 'POST':
        refresh_token = request.POST['refresh_token']

        # Verify the refresh token
        payload = verify_token(refresh_token)

        if payload:
            # Generate a new access token using the user ID from the refresh token
            access_token = generate_token({'user_id': payload['user_id']})
            return JsonResponse({'access_token': access_token})
        else:
            return JsonResponse({'error': 'Invalid refresh token'}, status=401)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def data_access(request):
    # Retrieve the JWT token from the request headers or cookies
    jwt_token = request.META.get('HTTP_AUTHORIZATION', None)

    if jwt_token:
        # Remove the 'Bearer ' prefix from the token
        jwt_token = jwt_token[7:]
        # Verify the JWT token
        payload = verify_token(jwt_token)

        if payload:
            try:
                user = User.objects.get(id=payload['user_id'])
                return JsonResponse({'user': model_to_dict(user)})
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid token'}, status=401)
    else:
        # Redirect the user to the login page if not authenticated
        return JsonResponse({'error': 'You are not allowed to access this'}, status=403)

############### 2FA ###################


@csrf_exempt
def login_2fa(request):
    if request.method == "POST":
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data or '{}')

        username = data.get('username')
        password = data.get('password')
        try:
            user = User.objects.get(username=username)
            # Check the password using Django's check_password
            if not check_password(password, user.password):
                return JsonResponse({"error": "Invalid credentials."}, status=401)
            return JsonResponse({"user_id": user.id}, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials."}, status=401)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


@csrf_exempt
def setup_2fa(request):
    if request.method == "POST":
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data or '{}')

        user_id = data.get('user_id')
        code = get_random_string(length=6, allowed_chars="0123456789")

        TwoFactorAuth.objects.create(user_id=user_id, code=code)

        return JsonResponse({}, status=200)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


@csrf_exempt
def verify_2fa(request):
    if request.method == "POST":
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data or '{}')

        user_id = data.get('user_id')
        code = data.get('code')

        try:
            # Retrieve the user's 2FA setup details from the database
            two_factor_auth = TwoFactorAuth.objects.get(user_id=user_id, code=code)
            two_factor_auth.delete()  # Remove the entry after successful verification
            token = generate_token({'user_id': user_id})
            return JsonResponse({"token": token}, status=200)
        except TwoFactorAuth.DoesNotExist:
            return JsonResponse({"error": "Invalid verification code."}, status=400)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)
