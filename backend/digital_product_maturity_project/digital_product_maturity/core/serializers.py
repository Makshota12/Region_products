from rest_framework import serializers
from .models import Product, Domain, Criterion, RatingScale, EvaluationSession, AssignedCriterion, EvaluationAnswer, Role, Profile
from django.contrib.auth.models import User

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = '__all__'

class CriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criterion
        fields = '__all__'

class RatingScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingScale
        fields = '__all__'

class EvaluationSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationSession
        fields = '__all__'

class AssignedCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedCriterion
        fields = '__all__'

class EvaluationAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationAnswer
        fields = '__all__'


# Сериализатор для чтения назначенных критериев (с ответами)
class AssignedCriterionReadSerializer(serializers.ModelSerializer):
    answer = EvaluationAnswerSerializer(read_only=True)
    criterion_name = serializers.CharField(source='criterion.name', read_only=True)
    criterion_description = serializers.CharField(source='criterion.description', read_only=True)
    criterion_weight = serializers.DecimalField(source='criterion.weight', max_digits=5, decimal_places=2, read_only=True)
    domain_name = serializers.CharField(source='criterion.domain.name', read_only=True)
    
    class Meta:
        model = AssignedCriterion
        fields = ['id', 'evaluation_session', 'criterion', 'criterion_name', 'criterion_description', 
                  'criterion_weight', 'domain_name', 'assigned_to', 'is_verified', 'verification_status',
                  'verification_comment', 'answer']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    role = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Profile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']