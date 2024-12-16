from concurrent import futures
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DB_CONFIG
import os
import server_services_pb2_grpc
import server_services_pb2
import grpc
import logging
import pg8000

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

# Consult the file "server_services_pb2_grpc" to find out the name of the Servicer class of the "SendFileService" service
class SendFileService(server_services_pb2_grpc.SendFileServiceServicer):
    def __init__(self, *args, **kwargs):
        pass

    def SendFile(self, request, context):
        os.makedirs(MEDIA_PATH, exist_ok=True)
        file_path = os.path.join(MEDIA_PATH, request.file_name + request.file_mime)
        ficheiro_em_bytes = request.file
        with open(file_path, 'wb') as f:
            f.write(ficheiro_em_bytes)
        logger.info(f"{DB_CONFIG['DBHOST']}:{DB_CONFIG['DBPORT']}", exc_info=True)
        
        # Establish connection to PostgreSQL
        try:
            # Connect to the database
            conn = pg8000.connect(
                user=DB_CONFIG['DBUSERNAME'], 
                password=DB_CONFIG['DBPASSWORD'], 
                host=DB_CONFIG['DBHOST'], 
                port=DB_CONFIG['DBPORT'], 
                database=DB_CONFIG['DBNAME']
            )
            cursor = conn.cursor()
            
            # SQL query to create a table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                coutry VARCHAR(100) UNIQUE NOT NULL,
                phone INT
            );
            """
            # Execute the SQL query to create the table
            cursor.execute(create_table_query)
            # Commit the changes
            conn.commit()
            
            # Name defined in the proto for the response
            return server_services_pb2.SendFileResponseBody(success=True)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            context.set_details(f"Failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileResponseBody(success=False)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    # Consult the file "server_services_pb2_grpc" to see the name of the function generated to add the service to the server
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
