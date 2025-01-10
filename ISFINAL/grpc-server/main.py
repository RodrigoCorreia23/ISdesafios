from concurrent import futures
import os
import server_services_pb2_grpc
import grpc
import logging
import pg8000
import pika
from file_processor import csv_to_xml_with_coordinates, validate_xml, find_coordinates, generate_xsd_from_xml, get_states_by_country
from server_services_pb2_grpc import FileServiceServicer
import server_services_pb2
from server_services_pb2 import ConvertCSVToXMLResponse
import xml.etree.ElementTree as ET

# Import environment variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "password")
DBNAME = os.getenv("DBNAME", "mydatabase")
DBUSERNAME = os.getenv("DBUSERNAME", "myuser")
DBPASSWORD = os.getenv("DBPASSWORD", "mypassword")
DBHOST = os.getenv("DBHOST", "db")
DBPORT = int(os.getenv("DBPORT", "5432"))
GRPC_SERVER_PORT = int(os.getenv("GRPC_SERVER_PORT", "50051"))

# Define media path
MEDIA_PATH = os.getenv("MEDIA_PATH", "/app/media")

# Define max workers for gRPC server
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

# SendFileService implementation
class SendFileService(server_services_pb2_grpc.SendFileServiceServicer):
    def SendFile(self, request, context):
        try:
            os.makedirs(MEDIA_PATH, exist_ok=True)
            file_path = os.path.join(MEDIA_PATH, request.file_name)
            with open(file_path, 'wb') as f:
                f.write(request.file)
            
            # Establish connection to PostgreSQL
            conn = pg8000.connect(
                user=DBUSERNAME, 
                password=DBPASSWORD, 
                host=DBHOST, 
                port=DBPORT, 
                database=DBNAME
            )
            cursor = conn.cursor()
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
            cursor.execute(create_table_query)
            conn.commit()
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
            file_chunks = []
            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name
                file_chunks.append(chunk.data)
                rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body=chunk.data)
            rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body="__EOF__")
            file_content = b"".join(file_chunks)
            file_path = os.path.join(MEDIA_PATH, file_name)
            with open(file_path, "wb") as f:
                f.write(file_content)
            return server_services_pb2.SendFileChunksResponse(success=True, message='File imported')
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return server_services_pb2.SendFileChunksResponse(success=False, message=str(e))

# FileService implementation
class FileService(server_services_pb2_grpc.FileServiceServicer):
    def ProcessCSV(self, request, context):
        try:
            csv_file_path = os.path.join(MEDIA_PATH, "received.csv")
            xml_file_path = os.path.join(MEDIA_PATH, "output.xml")
            xsd_file_path = os.path.join(MEDIA_PATH, "schema.xsd")
            os.makedirs(MEDIA_PATH, exist_ok=True)
            with open(csv_file_path, "wb") as f:
                f.write(request.file)

            regenerate_xml = False
            if os.path.exists(xml_file_path):
                try:
                    ET.parse(xml_file_path)
                except ET.ParseError:
                    regenerate_xml = True
            else:
                regenerate_xml = True

            if regenerate_xml:
                csv_to_xml_with_coordinates(csv_file_path, xml_file_path)

            if not os.path.exists(xsd_file_path):
                generate_xsd_from_xml(xml_file_path, xsd_file_path)

            is_valid = validate_xml(xml_file_path, xsd_file_path)
            coordinates = find_coordinates(xml_file_path)

            response = server_services_pb2.CoordinatesResponse(valid_xml=is_valid)
            for longitude, latitude in coordinates:
                coord = response.coordinates.add()
                coord.longitude = longitude
                coord.latitude = latitude

            return response
        except Exception as e:
            logger.error(f"Error in ProcessCSV: {e}", exc_info=True)
            context.set_details(f"Failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.CoordinatesResponse(valid_xml=False)

    def GetStatesByCountry(self, request, context):
        try:
            country_name = request.country
            xml_file_path = os.path.join(MEDIA_PATH, "output.xml")
            if not os.path.exists(xml_file_path):
                context.set_details(f"XML file not found: {xml_file_path}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_services_pb2.StatesResponse(states=[])

            states = get_states_by_country(xml_file_path, country_name)
            response = server_services_pb2.StatesResponse()
            response.states.extend(states)
            return response
        except Exception as e:
            logger.error(f"Error in GetStatesByCountry: {e}", exc_info=True)
            context.set_details(f"Failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.StatesResponse(states=[])
        
    def ConvertCSVToXML(self, request, context):
        try:
            # Caminho para salvar o arquivo CSV recebido
            csv_file_path = os.path.join("/app/media", request.file_name)
            with open(csv_file_path, 'wb') as f:
                f.write(request.file_content)

            # Caminho para o arquivo XML gerado
            xml_file_path = csv_file_path.replace('.csv', '.xml')

            # Função para converter CSV em XML (você precisa implementar esta função)
            csv_to_xml_with_coordinates(csv_file_path, xml_file_path)

            # Retornar a resposta
            return server_services_pb2.ConvertCSVToXMLResponse(
                success=True,
                xml_file_path=xml_file_path
            )
        except Exception as e:
            context.set_details(f"Error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.ConvertCSVToXMLResponse(success=False)

    def ConvertXMLToXSD(self, request, context):
        try:
            # Caminho para salvar o XML recebido
            xml_file_path = os.path.join(MEDIA_PATH, request.file_name)
            with open(xml_file_path, 'wb') as f:
                f.write(request.file_content)

            # Caminho para o arquivo XSD gerado
            xsd_file_path = xml_file_path.replace('.xml', '.xsd')

            # Gerar o XSD a partir do XML
            generate_xsd_from_xml(xml_file_path, xsd_file_path)

            # Retornar o caminho do XSD gerado
            return server_services_pb2.ConvertXMLToXSDResponse(
                success=True,
                xsd_file_path=xsd_file_path
            )
        except Exception as e:
            context.set_details(f"Error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.ConvertXMLToXSDResponse(success=False)

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=MAX_WORKERS),
        options=[
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
        ]
    )
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server_services_pb2_grpc.add_FileServiceServicer_to_server(FileService(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    logger.info("Starting GRPC server...")
    server.start()
    logger.info(f"GRPC server is running on port {GRPC_SERVER_PORT}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
