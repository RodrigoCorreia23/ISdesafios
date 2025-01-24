import grpc
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..grpc import server_services_pb2, server_services_pb2_grpc
from rest_api_server.settings import GRPC_PORT, GRPC_HOST
from django.db import connection

logger = logging.getLogger("WarehousesView")

class GetWarehousesView(APIView):
    def post(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT *
                    FROM motorcycle_sales
                """)
                rows = cursor.fetchall()

            warehouse_list = [
                {
                    "id": row[0],
                    "date": row[1],
                    "warehouse": row[2],
                    "client_type": row[3],
                    "product_line": row[4],
                    "quantity": row[5],
                    "unit_price": row[6],
                    "total": row[7],
                    "payment": row[8],
                    "latitude": row[9],
                    "longitude": row[10],
                }
                for row in rows
            ]

            return Response({
                "data": warehouse_list
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateWarehouseView(APIView):
    def put(self, request, id):
        try:
            latitude = request.data.get("latitude")
            longitude = request.data.get("longitude")

            if latitude is None or longitude is None:
                return Response(
                    {"error": "latitude and longitude are required fields."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE motorcycle_sales
                    SET latitude = %s, longitude = %s
                    WHERE id = %s
                    """,
                    [latitude, longitude, id],
                )

            return Response({"message": "Location updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            logging.error(f"Error updating warehouse location: {str(e)}")
            return Response(
                {"error": f"An error occurred while updating the location: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class FilterByProductLineView(APIView):
    def post(self, request):
        try:
            product_line = request.data.get("product_line")

            if not product_line:
                return Response(
                    {"error": "The 'product_line' field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, warehouse, product_line, latitude, longitude
                    FROM motorcycle_sales
                    WHERE product_line = %s
                """, [product_line])

                rows = cursor.fetchall()

            xml_data = "<warehouses>"
            for row in rows:
                xml_data += f"""
                    <warehouse>
                        <id>{row[0]}</id>
                        <warehouse_region>{row[1]}</warehouse_region>
                        <product_line>{row[2]}</product_line>
                        <latitude>{row[3]}</latitude>
                        <longitude>{row[4]}</longitude>
                    </warehouse>
                """
            xml_data += "</warehouses>"

            return Response(xml_data, status=status.HTTP_200_OK, content_type="application/xml")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)