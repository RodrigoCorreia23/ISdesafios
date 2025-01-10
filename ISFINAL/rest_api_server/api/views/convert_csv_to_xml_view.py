import os
import grpc
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..grpc import server_services_pb2, server_services_pb2_grpc
from rest_api_server.settings import GRPC_PORT, GRPC_HOST


logger = logging.getLogger("ConvertCSVToXMLView")

class ConvertCSVToXMLView(APIView):
    """
    View to handle the conversion of CSV to XML via gRPC.
    """
    def post(self, request):
        try:
            # Validate file input
            csv_file = request.FILES.get('file')
            if not csv_file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            file_name = csv_file.name
            file_content = csv_file.read()

            # Connect to gRPC server
            channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
            stub = server_services_pb2_grpc.FileServiceStub(channel)

            # Create gRPC request
            grpc_request = server_services_pb2.ConvertCSVToXMLRequest(
                file_name=file_name,
                file_content=file_content,
            )

            # Call the gRPC service
            response = stub.ConvertCSVToXML(grpc_request)

            if response.success:
                return Response({
                    "success": True,
                    "message": "CSV successfully converted to XML.",
                    "xml_file_path": response.xml_file_path,
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Failed to convert CSV to XML."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {e.details()}")
            return Response({
                "error": f"gRPC call failed: {e.details()}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
