from concurrent import futures
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH
import os
import server_services_pb2_grpc
import server_services_pb2
import grpc

class SendFileService(server_services_pb2_grpc.SendFileServiceServicer):
    def __init__(self, *args, **kwargs):
        pass

    def SendFile(self, request, context):
        os.makedirs(MEDIA_PATH, exist_ok=True)
        file_path = os.path.join(MEDIA_PATH, request.file_name + request.file_mime)
        ficheiro_em_bytes = request.file
        with open(file_path, 'wb') as f:
            f.write(ficheiro_em_bytes)
        # Nome definido no proto para a resposta "SendFileResponseBody"
        return server_services_pb2.SendFileResponseBody(success=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    
    # Adiciona o serviço ao servidor
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()
    print(f"Servidor gRPC rodando na porta {GRPC_SERVER_PORT}...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
