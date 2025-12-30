from rest_framework import serializers
from .models import Product, Domain, Criterion, RatingScale

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

