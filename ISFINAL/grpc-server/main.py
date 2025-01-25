from concurrent import futures
import os
import server_services_pb2_grpc
import grpc
import logging
import pg8000
import pika
from file_processor import csv_to_xml_with_coordinates, validate_xml, find_coordinates, generate_xsd_from_xml, \
    get_states_by_country, get_info_by_cardinalpoint


class SalesItem:
    def __init__(self, country, longitude, latitude):
        self.country = country
        self.longitude = longitude
        self.latitude = latitude
from server_services_pb2_grpc import FileServiceServicer
import server_services_pb2
from server_services_pb2 import ConvertCSVToXMLResponse, CountryResponse
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


# FileService implementation
class FileService(server_services_pb2_grpc.FileServiceServicer):
    
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
            xml_file_path = os.path.join(MEDIA_PATH, "Sales.xml")
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
        
    def GetSalesByCountryAndYear(self, request, context):
        try:
            # Extração dos parâmetros da requisição gRPC
            country_name = request.country
            year = request.year
            print(f"Country: {country_name}, Year: {year}")  # Depuração

            # Caminho para o arquivo XML
            xml_file_path = os.path.join(MEDIA_PATH, "Sales.xml")
            print(f"XML Path: {xml_file_path}")  # Depuração

            if not os.path.exists(xml_file_path):
                context.set_details(f"XML file not found: {xml_file_path}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_services_pb2.SalesResponse(sales=[])

            # Chamando a função auxiliar com o XPath correto
            sales = self.get_sales_by_country_and_year(xml_file_path, country_name, year)

            # Construindo a resposta gRPC
            response = server_services_pb2.SalesResponse()
            for sale in sales:
                response.sales.add(state=sale["state"], revenue=sale["revenue"])

            return response
        except Exception as e:
            logger.error(f"Error in GetSalesByCountryAndYear: {e}", exc_info=True)
            context.set_details(f"Failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SalesResponse(sales=[])



    def get_sales_by_country_and_year(xml_file_path, country, year):
        from lxml import etree
        tree = etree.parse(xml_file_path)

        # XPath atualizado para usar <item>
        xpath_query = f"//item[Country='{country}' and Year='{year}']"
        sales_elements = tree.xpath(xpath_query)

        sales = []
        for sale in sales_elements:
            state = sale.find("State").text
            revenue = float(sale.find("Revenue").text)
            sales.append({"state": state, "revenue": revenue})

        return sales



    def get_sales_by_country_and_year(self, xml_file_path, country, year):
        from lxml import etree
        tree = etree.parse(xml_file_path)

        # XPath para filtrar vendas por país e ano
        xpath_query = f"//item[Country='{country}' and Year='{year}']"
        sales_elements = tree.xpath(xpath_query)

        # Depuração: Exibir elementos encontrados
        print(f"XPath Query: {xpath_query}")
        print(f"Elements Found: {[etree.tostring(e, pretty_print=True).decode() for e in sales_elements]}")

        sales = []
        for sale in sales_elements:
            state = sale.find("State").text
            revenue = float(sale.find("Revenue").text)
            sales.append({"state": state, "revenue": revenue})

        return sales




    

    def GetInfoByCardinalPoint(self, request, context):
        try:
            _warehouse = request.warehouse
            xml_file_path = os.path.join(MEDIA_PATH, "MotorcycleSalesAnalysis.xml")

            if not os.path.exists(xml_file_path):
                context.set_details(f"XML file not found: {xml_file_path}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_services_pb2.CardinalPointResponse()

            cardinalpoints_data = get_info_by_cardinalpoint(xml_file_path, _warehouse)

            response = server_services_pb2.CardinalPointResponse()

            for point in cardinalpoints_data:
                entry = response.data.add()
                entry.date = point.get("date", "")
                entry.warehouse = point.get("warehouse", "")
                entry.client_type = point.get("client_type", "")
                entry.product_line = point.get("product_line", "")
                entry.quantity = point.get("quantity", 0)
                entry.unit_price = point.get("unit_price", 0.0)
                entry.total = point.get("total", 0.0)
                entry.payment = point.get("payment", "")
                entry.latitude = point.get("latitude", 0.0)
                entry.longitude = point.get("longitude", 0.0)

            return response

        except Exception as e:
            logger.error(f"Error in GetInfoByCardinalPoint: {e}", exc_info=True)
            context.set_details(f"Failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.CardinalPointResponse()

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

    def ExportToDatabase(self, request, context):
        try:
            xml_file_path = os.path.join(MEDIA_PATH, request.file_name)

            # Verificar se o arquivo XML existe
            if not os.path.exists(xml_file_path):
                context.set_details(f"Arquivo XML não encontrado: {xml_file_path}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_services_pb2.ExportToDatabaseResponse(
                    success=False,
                    message=f"Arquivo XML não encontrado: {xml_file_path}"
                )

            # Processar o arquivo Sales.xml
            if request.file_name == "Sales.xml":
                tree = ET.parse(xml_file_path)
                root = tree.getroot()

                # Conectar ao banco de dados PostgreSQL
                conn = pg8000.connect(
                    user=DBUSERNAME,
                    password=DBPASSWORD,
                    host=DBHOST,
                    port=DBPORT,
                    database=DBNAME
                )
                cursor = conn.cursor()

                # Criar tabela se não existir
                create_table_query = """
                CREATE TABLE IF NOT EXISTS cities (
                    id SERIAL PRIMARY KEY,
                    country VARCHAR(100),
                    state VARCHAR(100),
                    longitude FLOAT,
                    latitude FLOAT
                );
                """
                cursor.execute(create_table_query)
                conn.commit()

                # Inserir os dados no banco de dados
                for item in root.findall("item"):
                    country = item.findtext("Country")
                    state = item.findtext("State")
                    longitude = float(item.findtext("longitude", "0"))
                    latitude = float(item.findtext("latitude", "0"))

                    cursor.execute(
                        "INSERT INTO cities (country, state, longitude, latitude) VALUES (%s, %s, %s, %s)",
                        (country, state, longitude, latitude)
                    )

                conn.commit()
                cursor.close()
                conn.close()

                return server_services_pb2.ExportToDatabaseResponse(
                    success=True,
                    message="Data exported successfully from Sales.xml"
                )

            # Processar o arquivo MotorcycleSalesAnalysis.xml
            elif request.file_name == "MotorcycleSalesAnalysis.xml":
                tree = ET.parse(xml_file_path)
                root = tree.getroot()

                # Conectar ao banco de dados PostgreSQL
                conn = pg8000.connect(
                    user=DBUSERNAME,
                    password=DBPASSWORD,
                    host=DBHOST,
                    port=DBPORT,
                    database=DBNAME
                )
                cursor = conn.cursor()

                # Criar tabela se não existir
                create_table_query = """
                CREATE TABLE IF NOT EXISTS motorcycle_sales (
                    id SERIAL PRIMARY KEY,
                    date DATE,
                    warehouse VARCHAR(100),
                    client_type VARCHAR(100),
                    product_line VARCHAR(100),
                    quantity INT,
                    unit_price FLOAT,
                    total FLOAT,
                    payment VARCHAR(50),
                    latitude FLOAT,
                    longitude FLOAT
                );
                """
                cursor.execute(create_table_query)
                conn.commit()

                # Inserir os dados no banco de dados
                for item in root.findall("item"):
                    date = item.findtext("date")
                    warehouse = item.findtext("warehouse")
                    client_type = item.findtext("client_type")
                    product_line = item.findtext("product_line")
                    quantity = int(item.findtext("quantity", "0"))
                    unit_price = float(item.findtext("unit_price", "0"))
                    total = float(item.findtext("total", "0"))
                    payment = item.findtext("payment")
                    latitude = float(item.findtext("latitude", "0"))
                    longitude = float(item.findtext("longitude", "0"))

                    cursor.execute(
                        """
                        INSERT INTO motorcycle_sales 
                        (date, warehouse, client_type, product_line, quantity, unit_price, total, payment, latitude, longitude)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (date, warehouse, client_type, product_line, quantity, unit_price, total, payment, latitude,
                         longitude)
                    )

                conn.commit()
                cursor.close()
                conn.close()

                return server_services_pb2.ExportToDatabaseResponse(
                    success=True,
                    message="Data exported successfully from MotorcycleSalesAnalysis.xml"
                )

            else:
                # Caso o arquivo não seja reconhecido
                context.set_details("Unsupported file provided for ExportToDatabase.")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return server_services_pb2.ExportToDatabaseResponse(
                    success=False,
                    message="Unsupported file type. Only Sales.xml and MotorcycleSalesAnalysis.xml are supported."
                )
        except Exception as e:
            logger.error(f"Error in ExportToDatabase: {e}", exc_info=True)
            context.set_details(f"Error exporting the data: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.ExportToDatabaseResponse(
                success=False,
                message="Error exporting the data."
            )

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

    def GetStatesByCountry(self, request, context):
        try:
            xml_file_path = os.path.join(MEDIA_PATH, "Sales.xml")
            if not os.path.exists(xml_file_path):
                context.set_details(f"XML file not found: {xml_file_path}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_services_pb2.StatesResponse(states=[])

            # Buscar estados no arquivo XML
            states = get_states_by_country(xml_file_path, request.country)
            response = server_services_pb2.StatesResponse()
            response.states.extend(states)
            return response
        except Exception as e:
            logger.error(f"Error in GetStatesByCountry: {e}", exc_info=True)
            context.set_details(f"Error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.StatesResponse(states=[])
        
    def GetCountryLocations(self, request, context):
        # Carregar o XML
        tree = ET.parse('/app/media/Sales.xml') 
        root = tree.getroot()

        # Filtrar os dados do XML
        sales_items = []
        for item in root.findall('item'):
            country = item.find('Country').text
            if request.country and country != request.country:
                continue

            sales_items.append(SalesItem(
                country=country,
                longitude=float(item.find('longitude').text),
                latitude=float(item.find('latitude').text)
            ))

        # Retornar a resposta
        response = server_services_pb2.CountryResponse()
        response.sales_items.extend(sales_items)
        return response

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=MAX_WORKERS),
        options=[
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
        ]
    )
    server_services_pb2_grpc.add_FileServiceServicer_to_server(FileService(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    logger.info("Starting GRPC server...")
    server.start()
    logger.info(f"GRPC server is running on port {GRPC_SERVER_PORT}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
