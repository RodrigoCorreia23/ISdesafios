from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
class GetAllUsers(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()

