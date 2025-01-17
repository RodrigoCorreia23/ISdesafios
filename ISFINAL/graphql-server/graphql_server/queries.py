import graphene
from graphene_django.types import DjangoObjectType
from .models import Country

# Tipo para representar o modelo Country no GraphQL
class CountryType(DjangoObjectType):
    class Meta:
        model = Country
        fields = ("id", "country", "latitude", "longitude")

# Classe de Query
class Query(graphene.ObjectType):
    # Campo para listar todos os países ou buscar por nome
    countries = graphene.List(CountryType, name=graphene.String())

    def resolve_countries(self, info, name=None):
        # Filtrar por nome se o parâmetro for fornecido
        if name:
            return Country.objects.filter(country__icontains=name)
        return Country.objects.all()