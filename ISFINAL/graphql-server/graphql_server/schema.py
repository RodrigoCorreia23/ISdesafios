import graphene
from graphql_server.models import Country
from .mutations import Mutation
from .queries import Query

class CountryType(graphene.ObjectType):
        id = graphene.Int()
        country = graphene.String()
        latitude = graphene.Float()
        longitude = graphene.Float()

class Query(graphene.ObjectType):
    all_countries = graphene.List(CountryType)

    def resolve_all_countries(root, info):
        return Country.objects.all()


# Definir o schema
schema = graphene.Schema(query=Query, mutation=Mutation)



