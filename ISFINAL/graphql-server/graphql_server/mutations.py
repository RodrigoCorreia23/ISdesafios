import graphene
from .models import Country
from .queries import CountryType

# Mutation para criar um novo país
class CreateCountry(graphene.Mutation):
    class Arguments:
        country = graphene.String(required=True)
        latitude = graphene.Float(required=True)
        longitude = graphene.Float(required=True)

    country_obj = graphene.Field(CountryType)

    def mutate(self, info, country, latitude, longitude):
        country_obj = Country.objects.create(country=country, latitude=latitude, longitude=longitude)
        return CreateCountry(country_obj=country_obj)


# Mutation para atualizar um país existente
class UpdateCountry(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        country = graphene.String()
        latitude = graphene.Float()
        longitude = graphene.Float()

    country_obj = graphene.Field(CountryType)

    def mutate(self, info, id, country=None, latitude=None, longitude=None):
        try:
            country_obj = Country.objects.get(pk=id)
            if country:
                country_obj.country = country
            if latitude is not None:
                country_obj.latitude = latitude
            if longitude is not None:
                country_obj.longitude = longitude
            country_obj.save()
            return UpdateCountry(country_obj=country_obj)
        except Country.DoesNotExist:
            raise Exception("Country not found")


# Classe que contém todas as mutations
class Mutation(graphene.ObjectType):
    create_country = CreateCountry.Field()
    update_country = UpdateCountry.Field()