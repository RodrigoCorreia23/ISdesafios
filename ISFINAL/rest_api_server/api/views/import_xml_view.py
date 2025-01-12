from django.http import JsonResponse
from django.views import View
import grpc
from api.grpc import server_services_pb2, server_services_pb2_grpc
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class ImportXMLToDatabaseView(View):
    """
    Classe para importar dados de um arquivo XML para o banco de dados usando gRPC.
    """
    
    def post(self, request, *args, **kwargs):
        try:
            # Verificar se o arquivo foi enviado
            xml_file = request.FILES.get('file')
            if not xml_file:
                return JsonResponse({"success": False, "message": "Nenhum arquivo enviado."}, status=400)

            # Estabelecer conexão com o servidor gRPC
            channel = grpc.insecure_channel("grpc-server:50051")
            stub = server_services_pb2_grpc.FileServiceStub(channel)

            # Enviar o arquivo para o servidor gRPC
            response = stub.ConvertXMLToDatabase(
                server_services_pb2.ConvertXMLToDatabaseRequest(
                    file_name=xml_file.name,
                    file_content=xml_file.read()
                )
            )

            # Retornar a resposta do servidor gRPC
            return JsonResponse({"success": response.success, "message": response.message})
        
        except Exception as e:
            # Captura e trata erros durante o processamento
            return JsonResponse({"success": False, "message": f"Erro ao processar: {str(e)}"}, status=500)
