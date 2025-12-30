from rest_framework import viewsets
from .models import Product, Domain, Criterion, RatingScale
from .serializers import ProductSerializer, DomainSerializer, CriterionSerializer, RatingScaleSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

class CriterionViewSet(viewsets.ModelViewSet):
    queryset = Criterion.objects.all()
    serializer_class = CriterionSerializer

class RatingScaleViewSet(viewsets.ModelViewSet):
    queryset = RatingScale.objects.all()
    serializer_class = RatingScaleSerializer
