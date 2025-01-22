import graphene
from graphene_django.types import DjangoObjectType
from .models import Country
from .models import MotorcycleSales

# Tipo para representar o modelo Country no GraphQL
class CountryType(DjangoObjectType):
    class Meta:
        model = Country
        fields = ("id", "country", "latitude", "longitude")

# Tipo para representar o modelo MotorcycleSales no GraphQL
class MotorcycleSalesType(DjangoObjectType):
    class Meta:
        model = MotorcycleSales
        fields = (
            "id",
            "date",
            "warehouse",
            "client_type",
            "product_line",
            "quantity",
            "unit_price",
            "total",
            "payment",
            "latitude",
            "longitude",
        )

# Classe de Query
class Query(graphene.ObjectType):
    # Campo para listar todos os países ou procurar por nome
    countries = graphene.List(CountryType, name=graphene.String())
    motorcycle_sales = graphene.List(MotorcycleSalesType, warehouse=graphene.String())

    def resolve_countries(self, info, name=None):
        # Filtrar por nome se o parâmetro for fornecido
        if name:
            return Country.objects.filter(country__icontains=name)
        return Country.objects.all()

    def resolve_motorcycle_sales(self, info, warehouse=None):
        # Filtrar por warehouse se o parâmetro for fornecido
        if warehouse:
            return MotorcycleSales.objects.filter(warehouse__icontains=warehouse)
        return MotorcycleSales.objects.all()