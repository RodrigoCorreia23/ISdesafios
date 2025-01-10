import os
import grpc
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..grpc import server_services_pb2, server_services_pb2_grpc
from rest_api_server.settings import GRPC_PORT, GRPC_HOST

logger = logging.getLogger("ConvertXMLToXSDView")

class ConvertXMLToXSDView(APIView):
    def post(self, request):
        try:
            # Validar arquivo
            xml_file = request.FILES.get('file')
            if not xml_file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            file_name = xml_file.name
            file_content = xml_file.read()

            # Conectar ao servidor gRPC
            channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
            stub = server_services_pb2_grpc.FileServiceStub(channel)

            # Requisição gRPC
            grpc_request = server_services_pb2.ConvertXMLToXSDRequest(
                file_name=file_name,
                file_content=file_content
            )
            response = stub.ConvertXMLToXSD(grpc_request)

            if response.success:
                return Response({
                    "success": True,
                    "message": "XML successfully converted to XSD.",
                    "xsd_file_path": response.xsd_file_path,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to convert XML to XSD."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {e.details()}")
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
