from concurrent import futures
import os
import server_services_pb2_grpc
import server_services_pb2
import grpc
import logging
import pg8000
import pika
from file_processor import csv_to_xml_with_coordinates, validate_xml, find_coordinates, generate_xsd_from_xml, get_states_by_country  # Importa o módulo do processador
from server_services_pb2_grpc import add_FileServiceServicer_to_server
import server_services_pb2_grpc

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
MEDIA_PATH = os.getenv("MEDIA_PATH", r"C:\Users\User\OneDrive\Ambiente de Trabalho\E.I\IS")


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
                Date DATE,
                Day INT,
                Month VARCHAR(50),
                Year INT,
                Customer_Age INT,
                Age_Group VARCHAR(50),
                Customer_Gender CHAR(1),
                Country VARCHAR(100),
                State VARCHAR(100),
                Product_Category VARCHAR(100),
                Sub_Category VARCHAR(100),
                Product VARCHAR(100),
                Order_Quantity INT,
                Unit_Cost DECIMAL(10, 2),
                Unit_Price DECIMAL(10, 2),
                Profit DECIMAL(10, 2),
                Cost DECIMAL(10, 2),
                Revenue DECIMAL(10, 2)
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
        
        # Serviço FileService
import xml.etree.ElementTree as ET

class FileService(server_services_pb2_grpc.FileServiceServicer):
    def ProcessCSV(self, request, context):
        try:
            # Caminhos dos arquivos
            csv_file_path = os.path.join(MEDIA_PATH, "received.csv")
            xml_file_path = os.path.join(MEDIA_PATH, "output.xml")
            xsd_file_path = os.path.join(MEDIA_PATH, "schema.xsd")

            # Salvar o arquivo CSV recebido
            logger.info("A receber arquivo CSV...")
            os.makedirs(MEDIA_PATH, exist_ok=True)
            with open(csv_file_path, "wb") as f:
                f.write(request.file)
            logger.info(f"Arquivo CSV salvo em {csv_file_path}")

            # Verificar se o XML é válido
            regenerate_xml = False
            if os.path.exists(xml_file_path):
                try:
                    logger.info(f"Verificando validade do arquivo XML: {xml_file_path}")
                    ET.parse(xml_file_path)  # Tenta parsear o XML
                    logger.info(f"O arquivo XML é válido: {xml_file_path}")
                except ET.ParseError:
                    logger.warning(f"O arquivo XML está corrompido. Será regenerado: {xml_file_path}")
                    regenerate_xml = True
            else:
                regenerate_xml = True

            # Gerar o XML, se necessário
            if regenerate_xml:
                logger.info(f"Gerando XML: {xml_file_path}")
                csv_to_xml_with_coordinates(csv_file_path, xml_file_path)

            # Verificar e gerar o XSD, se necessário
            if not os.path.exists(xsd_file_path):
                logger.info(f"Arquivo XSD não encontrado. Gerando: {xsd_file_path}")
                generate_xsd_from_xml(xml_file_path, xsd_file_path)
            else:
                logger.info(f"O arquivo XSD já existe: {xsd_file_path}")

            # Validar o XML contra o XSD
            if not os.path.exists(xsd_file_path):
                logger.error(f"Arquivo XSD não encontrado: {xsd_file_path}")
                context.set_details("Arquivo XSD para validação não encontrado.")
                context.set_code(grpc.StatusCode.INTERNAL)
                return server_services_pb2.CoordinatesResponse(valid_xml=False)

            try:
                is_valid = validate_xml(xml_file_path, xsd_file_path)
                logger.info(f"Validação do XML: {is_valid}")
            except Exception as e:
                logger.error(f"Erro ao validar o XML: {e}", exc_info=True)
                context.set_details(f"Erro ao validar o XML: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return server_services_pb2.CoordinatesResponse(valid_xml=False)

            # Buscar coordenadas do XML
            try:
                coordinates = find_coordinates(xml_file_path)
                if not coordinates:
                    logger.warning("Nenhuma coordenada foi encontrada no XML gerado.")
                else:
                    logger.info(f"Coordenadas encontradas: {coordinates}")
            except Exception as e:
                logger.error(f"Erro ao buscar coordenadas no XML: {e}", exc_info=True)
                context.set_details(f"Erro ao buscar coordenadas: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return server_services_pb2.CoordinatesResponse(valid_xml=False)

            # Construir a resposta
            response = server_services_pb2.CoordinatesResponse()
            response.valid_xml = is_valid
            for longitude, latitude in coordinates:
                coord = response.coordinates.add()
                coord.longitude = longitude
                coord.latitude = latitude

            return response
        except Exception as e:
            logger.error(f"Erro no ProcessCSV: {str(e)}", exc_info=True)
            context.set_details(f"Failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.CoordinatesResponse(valid_xml=False)


# Novo método: GetStatesByCountry
    def GetStatesByCountry(self, request, context):
        """
        Retorna os estados associados a um país específico no XML.
        """
        try:
            country_name = request.country
            xml_file_path = os.path.join(MEDIA_PATH, "output.xml")

            if not os.path.exists(xml_file_path):
                context.set_details(f"Arquivo XML não encontrado: {xml_file_path}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_services_pb2.StatesResponse(states=[])

            # Chamar função para buscar estados
            states = get_states_by_country(xml_file_path, country_name)
            response = server_services_pb2.StatesResponse()
            response.states.extend(states)
            return response
        except Exception as e:
            logger.error(f"Erro ao buscar estados para o país {request.country}: {e}", exc_info=True)
            context.set_details(f"Erro ao processar solicitação: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.StatesResponse(states=[])


def serve():
    # Configurar o servidor gRPC com limites de mensagem aumentados
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=MAX_WORKERS),
        options=[
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50 MB
            ('grpc.max_send_message_length', 50 * 1024 * 1024),     # 50 MB
        ]
    )
    
    # Adicionar os serviços gRPC ao servidor
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server_services_pb2_grpc.add_FileServiceServicer_to_server(FileService(), server)
    
    # Configurar o endereço e a porta
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    
    # Iniciar o servidor
    logger.info("Starting GRPC server...")
    server.start()
    logger.info(f"GRPC server is running on port {GRPC_SERVER_PORT}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()