from django.db import models

class Country(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        db_table = 'cities'
        
