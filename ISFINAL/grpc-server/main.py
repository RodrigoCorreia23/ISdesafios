from concurrent import futures
import os
import server_services_pb2_grpc
import server_services_pb2
import grpc
import logging
import pg8000
import pika

# Import environment variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "password")
DBNAME = os.getenv("DBNAME", "mydatabase")
DBUSERNAME = os.getenv("DBUSERNAME", "myuser")
DBPASSWORD = os.getenv("DBPASSWORD", "mypassword")
DBHOST = os.getenv("DBHOST", "db")
DBPORT = os.getenv("DBPORT", "5432")
GRPC_SERVER_PORT = os.getenv("GRPC_SERVER_PORT", "50051")

# Define media path
MEDIA_PATH = os.getenv("MEDIA_PATH", "/path/to/media") #???????????? do we need this?

# Define max workers for gRPC server
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))

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
        logger.info(f"{DBHOST}:{DBPORT}", exc_info=True)
        
        # Establish connection to PostgreSQL
        try:
            # Connect to the database
            conn = pg8000.connect(
                user=DBUSERNAME, 
                password=DBPASSWORD, 
                host=DBHOST, 
                port=DBPORT, 
                database=DBNAME
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

    def SendFileChunks(self, request_iterator, context):
        try:
            rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
            ))
            rabbit_channel = rabbit_connection.channel()
            rabbit_channel.queue_declare(queue='csv_chunks')
            os.makedirs(MEDIA_PATH, exist_ok=True)
            file_name = None
            file_chunks = []  # Store all chunks in memory
            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name
                # Collect the file data chunks
                file_chunks.append(chunk.data)
                # Send data chunk to the worker
                rabbit_channel.basic_publish(exchange='',
                                             routing_key='csv_chunks', body=chunk.data)
            # Send info that the file stream ended
            rabbit_channel.basic_publish(exchange='',
                                         routing_key='csv_chunks', body="__EOF__")
            # Combine all chunks into a single bytes object
            file_content = b"".join(file_chunks)
            file_path = os.path.join(MEDIA_PATH, file_name)
            # Write the collected data to the file at the end
            with open(file_path, "wb") as f:
                f.write(file_content)
            return server_services_pb2.SendFileChunksResponse(success=True, message='File imported')
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return server_services_pb2.SendFileChunksResponse(success=False, message=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    # Consult the file "server_services_pb2_grpc" to see the name of the function generated to add the service to the server
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    logger.info("Starting GRPC server...")
    server.start()
    logger.info(f"GRPC server is running ")

    server.wait_for_termination()

if __name__ == '__main__':
    serve()