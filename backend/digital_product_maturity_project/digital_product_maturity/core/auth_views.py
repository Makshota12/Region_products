from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Регистрация нового пользователя"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response(
            {'error': 'Укажите username, email и password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Пользователь с таким именем уже существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Пользователь с таким email уже существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Создаем пользователя
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    # Профиль создается автоматически через signals в models.py

    return Response({
        'message': 'Пользователь успешно зарегистрирован',
        'username': user.username,
        'email': user.email
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Вход пользователя и получение JWT токенов"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Укажите username и password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'error': 'Неверные учетные данные'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Генерируем JWT токены
    refresh = RefreshToken.for_user(user)

    # Получаем роль пользователя
    try:
        profile = user.profile
        role = profile.role.get_name_display() if profile.role else 'Не назначена'
    except:
        role = 'Не назначена'

    return Response({
        'message': 'Вход выполнен успешно',
        'token': str(refresh.access_token),
        'refresh': str(refresh),
        'username': user.username,
        'email': user.email,
        'role': role
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_user(request):
    """Выход пользователя (blacklist токена)"""
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Выход выполнен успешно'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def current_user(request):
    """Получить информацию о текущем пользователе"""
    user = request.user
    
    if not user.is_authenticated:
        return Response(
            {'error': 'Пользователь не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        profile = user.profile
        role = profile.role.get_name_display() if profile.role else 'Не назначена'
    except:
        role = 'Не назначена'

    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': role,
        'is_staff': user.is_staff
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    """Вход через Google ID token и получение JWT токенов."""
    id_token = request.data.get('id_token')
    if not id_token:
        return Response(
            {'error': 'Отсутствует id_token'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with urlopen(f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}') as response:
            token_payload = json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError, ValueError):
        return Response(
            {'error': 'Недействительный Google токен'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Дополнительно валидируем клиента, если он задан на сервере.
    expected_aud = os.environ.get('GOOGLE_CLIENT_ID')
    if expected_aud and token_payload.get('aud') != expected_aud:
        return Response(
            {'error': 'Google токен выпущен для другого клиента'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    email = token_payload.get('email')
    email_verified = token_payload.get('email_verified')
    if not email or str(email_verified).lower() != 'true':
        return Response(
            {'error': 'Google аккаунт должен иметь подтвержденный email'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.filter(email=email).first()
    if not user:
        base_username = re.sub(r'[^a-zA-Z0-9_]', '_', email.split('@')[0])[:120] or 'google_user'
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}_{suffix}'
            suffix += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=None
        )
        user.set_unusable_password()
        user.save()

    refresh = RefreshToken.for_user(user)

    try:
        profile = user.profile
        role = profile.role.get_name_display() if profile.role else 'Не назначена'
    except Exception:
        role = 'Не назначена'

    return Response({
        'message': 'Вход через Google выполнен успешно',
        'token': str(refresh.access_token),
        'refresh': str(refresh),
        'username': user.username,
        'email': user.email,
        'role': role
    }, status=status.HTTP_200_OK)

