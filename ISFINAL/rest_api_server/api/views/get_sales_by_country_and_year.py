import grpc
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..grpc import server_services_pb2, server_services_pb2_grpc
from rest_api_server.settings import GRPC_PORT, GRPC_HOST

logger = logging.getLogger("GetSalesByCountryAndYearView")

class GetSalesByCountryAndYearView(APIView):
    def post(self, request):
        try:
            # Extrair o nome do país e o ano do corpo da requisição
            country = request.data.get("country")
            year = request.data.get("year")
            if not country or not year:
                return Response({"error": "Country and year are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Conectar ao servidor gRPC
            channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
            stub = server_services_pb2_grpc.FileServiceStub(channel)

            # Criar a requisição gRPC
            grpc_request = server_services_pb2.SalesRequest(country=country, year=year)

            # Chamar o método gRPC
            response = stub.GetSalesByCountryAndYear(grpc_request)

            # Converter a resposta para JSON serializável
            sales_list = [{"state": sale.state, "revenue": sale.revenue} for sale in response.sales]

            return Response({
                "country": country,
                "year": year,
                "sales": sales_list
            }, status=status.HTTP_200_OK)

        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {e.details()}")
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
