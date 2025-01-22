import grpc
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..grpc import server_services_pb2, server_services_pb2_grpc
from rest_api_server.settings import GRPC_PORT, GRPC_HOST

logger = logging.getLogger("GetInfoByCardinalPointView")

class GetInfoByCardinalPointView(APIView):
    def post(self, request):
        try:
            # Extrair o ponto cardeal do corpo da requisição
            warehouse = request.data.get("warehouse")
            if not warehouse:
                return Response({"error": "Warehouse (cardinal point) is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Conectar ao servidor gRPC
            channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
            stub = server_services_pb2_grpc.FileServiceStub(channel)

            # Criar a requisição gRPC
            grpc_request = server_services_pb2.CardinalPointRequest(warehouse=warehouse)

            # Chamar o método gRPC
            response = stub.GetInfoByCardinalPoint(grpc_request)

            # Converter a resposta para JSON serializável
            warehouse_list = [
                {
                    "date": entry.date,
                    "warehouse": entry.warehouse,
                    "client_type": entry.client_type,
                    "product_line": entry.product_line,
                    "quantity": entry.quantity,
                    "unit_price": entry.unit_price,
                    "total": entry.total,
                    "payment": entry.payment,
                    "latitude": entry.latitude,
                    "longitude": entry.longitude,
                }
                for entry in response.data
            ]

            return Response({
                "warehouse": warehouse,
                "data": warehouse_list
            }, status=status.HTTP_200_OK)

        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {e.details()}")
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)