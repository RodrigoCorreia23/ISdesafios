import graphene
from .models import Country
from .queries import CountryType
from .models import MotorcycleSales
from .queries import MotorcycleSalesType

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

class UpdateMotorcycleSale(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
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

    motorcycle_sales = graphene.Field(MotorcycleSalesType)

    def mutate(
            self, info, id, date=None, warehouse=None, client_type=None,
            product_line=None, quantity=None, unit_price=None, total=None,
            payment=None, latitude=None, longitude=None
    ):
        try:
            motorcycle_sales = MotorcycleSales.objects.get(pk=id)
            if date:
                motorcycle_sales.date = date
            if warehouse:
                motorcycle_sales.warehouse = warehouse
            if client_type:
                motorcycle_sales.client_type = client_type
            if product_line:
                motorcycle_sales.product_line = product_line
            if quantity is not None:
                motorcycle_sales.quantity = quantity
            if unit_price is not None:
                motorcycle_sales.unit_price = unit_price
            if total is not None:
                motorcycle_sales.total = total
            if payment:
                motorcycle_sales.payment = payment
            if latitude is not None:
                motorcycle_sales.latitude = latitude
            if longitude is not None:
                motorcycle_sales.longitude = longitude
            motorcycle_sales.save()
            return UpdateMotorcycleSale(motorcycle_sales=motorcycle_sales)
        except MotorcycleSales.DoesNotExist:
            raise Exception("Motorcycle sales record not found")

# Classe que contém todas as mutations
class Mutation(graphene.ObjectType):
    update_country = UpdateCountry.Field()
    update_motorcycle_sale = UpdateMotorcycleSale.Field()