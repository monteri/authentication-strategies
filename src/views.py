from datetime import datetime, timedelta
import requests
from django.conf import settings

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.core.signing import Signer, BadSignature
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

from .models import CustomSession


def sign_token(token):
    signer = Signer()
    return signer.sign(token)


def unsign_token(signed_token):
    signer = Signer()
    try:
        return signer.unsign(signed_token)
    except:
        return None


def create_session(user_id):
    # Generate a random session key
    session_key = get_random_string(length=40)
    signed_key = sign_token(session_key)
    # Calculate the session's expiration date (set to 1 hour in this example)
    expire_date = datetime.now() + timedelta(hours=1)
    # Create the CustomSession record in the database
    CustomSession.objects.create(session_key=session_key, data=user_id, expire_date=expire_date)
    return signed_key


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return HttpResponse('Username already taken')
        else:
            # Use Django's make_password to securely hash the password
            hashed_password = make_password(password)
            # Create a new user with the provided credentials
            user = User.objects.create(username=username, password=hashed_password)
            user.save()
            return HttpResponse('User created successfully')

    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
            # Check the password using Django's check_password
            if check_password(password, user.password):
                # Create a session and get the session key
                session_key = create_session(user.id)
                response = HttpResponse('Login successful')
                response.set_cookie('auth_token', session_key, max_age=3600, httponly=True)
                return response
            else:
                return HttpResponse('Invalid credentials')
        except User.DoesNotExist:
            return HttpResponse('Invalid credentials')

    return render(request, 'login.html')


def data_access(request):
    print(request.COOKIES)
    session_signed_key = request.COOKIES.get('auth_token', None)
    print('session_signed_key', session_signed_key)
    if session_signed_key:
        try:
            session_key = unsign_token(session_signed_key)
            print('session_key', session_key)
            session = CustomSession.objects.get(pk=session_key)
            user = User.objects.get(id=session.data)
            return render(request, 'data_access.html', {'user': user})
        except (CustomSession.DoesNotExist, ValueError):
            return HttpResponse('Invalid session or token')
        except User.DoesNotExist:
            return HttpResponse('User not found')
        except BadSignature:
            return HttpResponse('Invalid token')
    else:
        # Redirect the user to the login page if not authenticated
        return redirect('login')


def logout(request):
    response = HttpResponse('Logged out')
    response.delete_cookie('auth_token')
    return response


############### GOOGLE ######################

def google_login(request):
    # Construct the Google OAuth authorization URL
    auth_endpoint = 'https://accounts.google.com/o/oauth2/auth'
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': 'http://localhost:8000/oauth2callback/',
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
    }
    redirect_url = f'{auth_endpoint}?{"&".join(f"{key}={value}" for key, value in params.items())}'
    return redirect(redirect_url)


def google_callback(request):
    code = request.GET.get('code')
    if not code:
        return render(request, 'oauth_error.html', {'error_message': 'Google authentication failed.'})

    # Exchange the authorization code for an access token
    token_url = 'https://oauth2.googleapis.com/token'
    params = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': 'http://localhost:8000/oauth2callback/',
        'grant_type': 'authorization_code',
    }

    response = requests.post(token_url, data=params)
    if response.status_code == 200:
        data = response.json()
        access_token = data['access_token']

        user_info_url = 'https://openidconnect.googleapis.com/v1/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}

        user_info_response = requests.get(user_info_url, headers=headers)
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            print('user_info_response', user_info_response, user_info)
            user_email = user_info.get('email')
            user, _ = User.objects.get_or_create(username=user_email)
            session_key = create_session(user.id)
            response = HttpResponse('Login successful')
            response.set_cookie('auth_token', session_key, max_age=3600, httponly=True)
            return response
        else:
            return render(request, 'oauth_error.html', {'error_message': 'Failed to get user information.'})
    else:
        return render(request, 'oauth_error.html', {'error_message': 'Failed to get access token from Google.'})

