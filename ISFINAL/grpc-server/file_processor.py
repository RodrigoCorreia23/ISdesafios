from geopy.geocoders import Nominatim
import csv
import xml.etree.ElementTree as ET
from lxml import etree
import pandas as pd
import time
import logging
import os

# Configurar o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def csv_to_xml_with_coordinates(csv_file_path, xml_output_path):
    """
    Converte um arquivo CSV em XML e adiciona longitude e latitude com base em País e Estado.
    """
    if os.path.exists(xml_output_path):
        logger.info(f"O arquivo XML já existe: {xml_output_path}. Pulando a geração do XML.")
        return  # Retorna diretamente se o arquivo já existe
    
    logger.info(f"Iniciando conversão de CSV para XML. Arquivo CSV: {csv_file_path}")
    geolocator = Nominatim(user_agent="my_app/1.0")

    # Criar o arquivo XML e escrever a tag raiz
    with open(xml_output_path, "wb") as xml_file:
        xml_file.write(b'<?xml version="1.0" encoding="UTF-8"?>\n<root>\n')

        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            logger.info(f"Colunas encontradas no CSV: {reader.fieldnames}")

            for row in reader:
                item = ET.Element("item")
                for key, value in row.items():
                    child = ET.SubElement(item, key)
                    child.text = value or ""

                # Buscar coordenadas com base em "Country" e "State"
                country = row.get("Country")
                state = row.get("State")
                if country and state:
                    try:
                        location = geolocator.geocode(f"{state}, {country}", timeout=10)
                        if location:
                            ET.SubElement(item, "longitude").text = str(location.longitude)
                            ET.SubElement(item, "latitude").text = str(location.latitude)
                            logger.info(f"Coordenadas adicionadas: {state}, {country} -> "
                                        f"({location.latitude}, {location.longitude})")
                        else:
                            logger.warning(f"Coordenadas não encontradas para {state}, {country}")
                    except Exception as e:
                        logger.error(f"Erro ao buscar coordenadas para {state}, {country}: {e}")

                # Escrever o item no arquivo XML
                xml_file.write(ET.tostring(item, encoding="utf-8"))

                # Aguardar para evitar bloqueio na API
                time.sleep(1)

        # Fechar a tag raiz
        xml_file.write(b'</root>\n')
    logger.info(f"Arquivo XML gerado progressivamente em: {xml_output_path}")




def validate_xml(xml_file_path, xsd_file_path):
    """
    Valida um arquivo XML contra um esquema XSD.
    """
    try:
        # Abrir e carregar o XSD como bytes
        with open(xsd_file_path, 'rb') as xsd_file:  # Alterado para 'rb' (modo binário)
            schema_root = etree.XML(xsd_file.read())

        schema = etree.XMLSchema(schema_root)
        parser = etree.XMLParser(schema=schema)

        # Validar o XML
        with open(xml_file_path, 'rb') as xml_file:  # Alterado para 'rb' (modo binário)
            etree.fromstring(xml_file.read(), parser)
        
        return True
    except etree.XMLSchemaError as e:
        logger.error(f"Erro de validação do XML: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro ao validar o XML: {e}")
        raise


def find_coordinates(xml_file_path):
    """
    Busca longitude e latitude no arquivo XML usando XPath.
    """
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    coordinates = []
    for item in root.findall("item"):
        longitude = item.find("longitude")
        latitude = item.find("latitude")
        if longitude is not None and latitude is not None:
            coordinates.append((longitude.text, latitude.text))

    return coordinates


def generate_xsd_from_xml(xml_file_path, xsd_output_path):
    logger.info(f"Iniciando geração do XSD a partir do XML. Arquivo XML: {xml_file_path}")
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Criar o elemento raiz do XSD
        schema = ET.Element("xs:schema", attrib={
            "xmlns:xs": "http://www.w3.org/2001/XMLSchema",
            "elementFormDefault": "qualified"
        })

        # Adicionar o elemento principal
        root_element = ET.SubElement(schema, "xs:element", name="root")
        complex_type = ET.SubElement(root_element, "xs:complexType")
        sequence = ET.SubElement(complex_type, "xs:sequence")

        # Definir o elemento <item>
        item_element = ET.SubElement(sequence, "xs:element", name="item", minOccurs="0", maxOccurs="unbounded")
        item_complex_type = ET.SubElement(item_element, "xs:complexType")
        item_sequence = ET.SubElement(item_complex_type, "xs:sequence")

        # Inferir os tipos de dados para cada elemento filho dentro de <item>
        for item in root.findall("item"):
            for child in item:
                if child.tag not in [elem.get("name") for elem in item_sequence.findall("xs:element")]:
                    xsd_type = infer_xsd_type(child.text)
                    logger.info(f"Elemento '{child.tag}' inferido como '{xsd_type}'")
                    ET.SubElement(item_sequence, "xs:element", name=child.tag, type=xsd_type, minOccurs="0")

        # Escrever o XSD em um arquivo
        xsd_tree = ET.ElementTree(schema)
        xsd_tree.write(xsd_output_path, encoding="utf-8", xml_declaration=True)
        logger.info(f"XSD gerado com sucesso: {xsd_output_path}")

    except Exception as e:
        logger.error(f"Erro ao gerar o arquivo XSD: {e}", exc_info=True)
        raise





def infer_xsd_type(value):
    """
    Infere o tipo XSD com base no valor fornecido.
    """
    try:
        int(value)
        return "xs:integer"
    except ValueError:
        try:
            float(value)
            return "xs:decimal"
        except ValueError:
            if isinstance(value, str) and value.lower() in ["true", "false"]:
                return "xs:boolean"
            return "xs:string"
        
        
        
def get_states_by_country(xml_file_path, country_name):
    """
    Retorna todos os estados associados a um país específico no XML.
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        states = set()  # Usar set para evitar duplicados

        for item in root.findall("item"):
            country = item.find("Country")
            state = item.find("State")
            if country is not None and state is not None:
                if country.text.strip().lower() == country_name.strip().lower():
                    states.add(state.text.strip())

        return list(states)
    except Exception as e:
        logger.error(f"Erro ao buscar estados pelo país {country_name}: {e}")
        return []


if __name__ == '__main__':
    # Definir o caminho da mídia
    MEDIA_PATH = os.getenv("MEDIA_PATH", r"C:\Users\User\OneDrive\Ambiente de Trabalho\E.I\IS") 

    # Caminhos dos arquivos
    csv_file_path = os.path.join(MEDIA_PATH, "received.csv")
    xml_output_path = os.path.join(MEDIA_PATH, "output.xml")
    xsd_output_path = os.path.join(MEDIA_PATH, "schema.xsd")

    # Verificar se o XML já existe
    if os.path.exists(xml_output_path):
        logger.info(f"O arquivo XML já existe: {xml_output_path}. Pulando a geração do XML.")
    else:
        logger.info(f"Arquivo XML não encontrado. Gerando o XML: {xml_output_path}")
        csv_to_xml_with_coordinates(csv_file_path, xml_output_path)

    # Verificar se o XSD já existe
    if os.path.exists(xsd_output_path):
        logger.info(f"O arquivo XSD já existe: {xsd_output_path}. Pulando a geração do XSD.")
    else:
        logger.info(f"Arquivo XSD não encontrado. Gerando o XSD: {xsd_output_path}")
        try:
            generate_xsd_from_xml(xml_output_path, xsd_output_path)
        except Exception as e:
            logger.error(f"Erro ao gerar o arquivo XSD: {e}", exc_info=True)

    # Validar o XML
    try:
        is_valid = validate_xml(xml_output_path, xsd_output_path)
        if is_valid:
            logger.info("O XML é válido contra o XSD.")
        else:
            logger.warning("O XML não é válido contra o XSD.")
    except Exception as e:
        logger.error(f"Erro ao validar XML contra o XSD: {e}", exc_info=True)


    # Consulta XPath
    country_name = "USA"  # Substitua pelo nome do país que deseja buscar
    print(f"Buscando estados do país {country_name} no XML...")
    states = get_states_by_country(xml_output_path, country_name)
    print(f"Estados encontrados: {states}")

