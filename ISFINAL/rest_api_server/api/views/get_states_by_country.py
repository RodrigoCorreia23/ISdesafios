import grpc
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..grpc import server_services_pb2, server_services_pb2_grpc
from rest_api_server.settings import GRPC_PORT, GRPC_HOST

logger = logging.getLogger("GetStatesByCountryView")

class GetStatesByCountryView(APIView):
    def post(self, request):
        try:
            # Extrair o nome do país do corpo da requisição
            country = request.data.get("country")
            if not country:
                return Response({"error": "Country is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Conectar ao servidor gRPC
            channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
            stub = server_services_pb2_grpc.FileServiceStub(channel)

            # Criar a requisição gRPC
            grpc_request = server_services_pb2.StatesRequest(country=country)

            # Chamar o método gRPC
            response = stub.GetStatesByCountry(grpc_request)

            # Converter a resposta para JSON serializável
            states_list = list(response.states)

            return Response({
                "country": country,
                "states": states_list
            }, status=status.HTTP_200_OK)

        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {e.details()}")
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

