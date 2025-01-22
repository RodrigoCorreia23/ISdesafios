from django.db import models

class Country(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        db_table = 'cities'

class MotorcycleSales(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    warehouse = models.CharField(max_length=255)
    client_type = models.CharField(max_length=255)
    product_line = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    total = models.FloatField()
    payment = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        db_table = 'motorcycle_sales'
        
