import graphene
from graphql_server.models import Country
from graphql_server.models import MotorcycleSales
from .mutations import Mutation

class CountryType(graphene.ObjectType):
        id = graphene.Int()
        country = graphene.String()
        latitude = graphene.Float()
        longitude = graphene.Float()

class MotorcycleSalesType(graphene.ObjectType):
    id = graphene.Int()
    date = graphene.Date()
    warehouse = graphene.String()
    client_type = graphene.String()
    product_line = graphene.String()
    quantity = graphene.Int()
    unit_price = graphene.Float()
    total = graphene.Float()
    payment = graphene.String()
    latitude = graphene.Float()
    longitude = graphene.Float()

class Query(graphene.ObjectType):
    countries = graphene.List(
        CountryType,
        country=graphene.String()
    )
    motorcycle_sales = graphene.List(
        MotorcycleSalesType,
        warehouse=graphene.String()
    )

    def resolve_countries(root, info, country=None):
        if country:
            return Country.objects.filter(country__icontains=country)
        return Country.objects.all()

    def resolve_motorcycle_sales(root, info, warehouse=None):
        if warehouse:
            return MotorcycleSales.objects.filter(warehouse=warehouse)
        return MotorcycleSales.objects.all()


# Definir o schema
schema = graphene.Schema(query=Query, mutation=Mutation)



