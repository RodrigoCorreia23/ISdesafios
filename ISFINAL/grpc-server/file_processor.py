import csv
import xml.etree.ElementTree as ET
import xmlschema
import os
import logging
import pg8000

# Configuração do logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self, schema_path):
        self.schema_path = schema_path  # Caminho para o arquivo XSD

    def convert_csv_to_xml(self, csv_file_path, xml_file_path):
        """
        Converte o arquivo CSV para XML.
        """
        try:
            with open(csv_file_path, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                root = ET.Element("Records")
                for row in reader:
                    record = ET.SubElement(root, "Record")
                    for key, value in row.items():
                        field = ET.SubElement(record, key)
                        field.text = value
                tree = ET.ElementTree(root)
                tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)
                logger.info(f"XML gerado em {xml_file_path}")
        except Exception as e:
            logger.error(f"Erro ao converter CSV para XML: {str(e)}")
            raise

    def validate_xml(self, xml_file_path):
        """
        Valida o XML gerado contra o schema XSD.
        """
        try:
            schema = xmlschema.XMLSchema(self.schema_path)
            if not schema.is_valid(xml_file_path):
                raise ValueError("A validação do XML falhou.")
        except Exception as e:
            logger.error(f"Erro ao validar XML: {str(e)}")
            raise

    def insert_data_into_db(self, csv_file_path):
        """
        Insere os dados do CSV no banco de dados PostgreSQL.
        """
        try:
            conn = pg8000.connect(
                user=os.getenv('DBUSERNAME'),
                password=os.getenv('DBPASSWORD'),
                host=os.getenv('DBHOST'),
                port=os.getenv('DBPORT'),
                database=os.getenv('DBNAME')
            )
            cursor = conn.cursor()

            # Criação da tabela
            create_table_query = """
            CREATE TABLE IF NOT EXISTS Sales (
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

            # Inserir os dados do CSV na tabela
            with open(csv_file_path, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    insert_query = """
                    INSERT INTO Sales (Date, Day, Month, Year, Customer_Age, Age_Group, Customer_Gender, Country, State, 
                    Product_Category, Sub_Category, Product, Order_Quantity, Unit_Cost, Unit_Price, Profit, Cost, Revenue)
                    VALUES (%(Date)s, %(Day)s, %(Month)s, %(Year)s, %(Customer_Age)s, %(Age_Group)s, %(Customer_Gender)s, 
                    %(Country)s, %(State)s, %(Product_Category)s, %(Sub_Category)s, %(Product)s, %(Order_Quantity)s, 
                    %(Unit_Cost)s, %(Unit_Price)s, %(Profit)s, %(Cost)s, %(Revenue)s);
                    """
                    cursor.execute(insert_query, row)
                conn.commit()

            conn.close()
            logger.info("Dados inseridos com sucesso no banco de dados.")
        except Exception as e:
            logger.error(f"Erro ao inserir dados no banco de dados: {str(e)}")
            raise
