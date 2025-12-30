from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Role, Profile


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

