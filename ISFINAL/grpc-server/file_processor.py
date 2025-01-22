from geopy.geocoders import Nominatim
import csv
import xml.etree.ElementTree as ET
from lxml import etree
import pandas as pd
import time
import logging
import os
import random

# Configurar o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def csv_to_xml_with_coordinates(csv_file_path, xml_output_path):
    if os.path.exists(xml_output_path):
        logger.info(f"XML file already exists: {xml_output_path}.")
        return

    logger.info(f"Starting CSV to XML conversion. CSV file: {csv_file_path}")
    geolocator = Nominatim(user_agent="my_app/1.0")

    def process_row_with_country_state(row, geolocator, item):
        country = row.get("Country")
        state = row.get("State")

        if country and state:
            try:
                location = geolocator.geocode(f"{state}, {country}", timeout=10)
                if location:
                    ET.SubElement(item, "longitude").text = str(location.longitude)
                    ET.SubElement(item, "latitude").text = str(location.latitude)
                    logger.info(f"Coordinates added: {state}, {country} -> "
                                f"({location.latitude}, {location.longitude})")
                else:
                    logger.warning(f"Coordinates not found for {state}, {country}")
            except Exception as e:
                logger.error(f"Error searching for coordinates for {state}, {country}: {e}")
            finally:
                time.sleep(1)

    def process_row_with_warehouse(row, item):
        regions_usa = {
            "North": {"latitude_range": (40.0, 49.0), "longitude_range": (-125.0, -75.0)},
            "South": {"latitude_range": (24.0, 33.0), "longitude_range": (-125.0, -75.0)},
            "East": {"latitude_range": (24.0, 49.0), "longitude_range": (-75.0, -66.0)},
            "West": {"latitude_range": (24.0, 49.0), "longitude_range": (-125.0, -100.0)},
            "Central": {"latitude_range": (33.0, 40.0), "longitude_range": (-100.0, -85.0)},
        }

        warehouse_location = row.get("warehouse")
        if warehouse_location:
            region = regions_usa.get(warehouse_location)
            if region:
                latitude = round(random.uniform(*region["latitude_range"]), 6)
                longitude = round(random.uniform(*region["longitude_range"]), 6)
                logger.info(f"Coordinates generated for '{warehouse_location}': ({latitude}, {longitude})")
            else:
                logger.warning(f"Region '{warehouse_location}' not recognized. Default values will be assigned.")
                latitude, longitude = 0.0, 0.0
            ET.SubElement(item, "latitude").text = str(latitude)
            ET.SubElement(item, "longitude").text = str(longitude)

    def create_item_from_row(row):
        item = ET.Element("item")
        for key, value in row.items():
            child = ET.SubElement(item, key)
            child.text = value or ""
        return item

    with open(xml_output_path, "wb") as xml_file:
        xml_file.write(b'<?xml version="1.0" encoding="UTF-8"?>\n<root>\n')

        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            fieldnames = reader.fieldnames

            if not fieldnames:
                logger.warning("CSV is empty or has no headers. No action will be taken.")
                return

            logger.info(f"Columns found in CSV: {fieldnames}")

            for row in reader:
                item = create_item_from_row(row)

                if 'Country' in fieldnames and 'State' in fieldnames:
                    process_row_with_country_state(row, geolocator, item)
                elif 'warehouse' in fieldnames:
                    process_row_with_warehouse(row, item)
                else:
                    logger.warning(
                        "The CSV does not contain the expected columns ('Country', 'State' or 'warehouse'). No action will be taken.")
                    return

                xml_file.write(ET.tostring(item, encoding="utf-8"))

        xml_file.write(b'</root>\n')

    logger.info(f"Conversion completed. XML saved in: {xml_output_path}")

def validate_xml(xml_file_path, xsd_file_path):
    try:
        # Open and load XSD as bytes
        with open(xsd_file_path, 'rb') as xsd_file:
            schema_root = etree.XML(xsd_file.read())

        schema = etree.XMLSchema(schema_root)
        parser = etree.XMLParser(schema=schema)

        # Validate the XML
        with open(xml_file_path, 'rb') as xml_file:
            etree.fromstring(xml_file.read(), parser)
        
        return True
    except etree.XMLSchemaError as e:
        logger.error(f"XML validation error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error validating XML: {e}")
        raise

def find_coordinates(xml_file_path):
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
    logger.info(f"Starting XSD generation from XML. XML file: {xml_file_path}")
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
                    logger.info(f"Element '{child.tag}' inferred as '{xsd_type}'")
                    ET.SubElement(item_sequence, "xs:element", name=child.tag, type=xsd_type, minOccurs="0")

        # Escrever o XSD em um arquivo
        xsd_tree = ET.ElementTree(schema)
        xsd_tree.write(xsd_output_path, encoding="utf-8", xml_declaration=True)
        logger.info(f"XSD generated successfully: {xsd_output_path}")

    except Exception as e:
        logger.error(f"Error generating XSD file: {e}", exc_info=True)
        raise

def infer_xsd_type(value):
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
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        states = set()

        for item in root.findall("item"):
            country = item.find("Country")
            state = item.find("State")
            if country is not None and state is not None:
                if country.text.strip().lower() == country_name.strip().lower():
                    states.add(state.text.strip())

        return list(states)
    except Exception as e:
        logger.error(f"Error searching for states by country {country_name}: {e}")
        return []

def get_info_by_cardinalpoint(xml_file_path, warehouse):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        cardinalpoint_data = []

        for item in root.findall("item"):
            item_warehouse = item.find("warehouse")
            if item_warehouse is not None and item_warehouse.text.strip().lower() == warehouse.strip().lower():
                cardinalpoint_entry = {
                    "date": item.findtext("date", "").strip(),
                    "warehouse": item.findtext("warehouse", "").strip(),
                    "client_type": item.findtext("client_type", "").strip(),
                    "product_line": item.findtext("product_line", "").strip(),
                    "quantity": int(item.findtext("quantity", "0").strip()),
                    "unit_price": float(item.findtext("unit_price", "0.0").strip()),
                    "total": float(item.findtext("total", "0.0").strip()),
                    "payment": item.findtext("payment", "").strip()
                }
                cardinalpoint_data.append(cardinalpoint_entry)

        return cardinalpoint_data
    except Exception as e:
        logger.error(f"Error retrieving data by cardinal point [{warehouse}]: {e}", exc_info=True)
        return []

if __name__ == '__main__':
    # Definir o caminho da mídia
    MEDIA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'media')

    # Caminhos dos arquivos
    csv_file_path = os.path.join(MEDIA_PATH, "received.csv")
    xml_output_path = os.path.join(MEDIA_PATH, "output.xml")
    xsd_output_path = os.path.join(MEDIA_PATH, "schema.xsd")

    # Verificar se o XML já existe
    if os.path.exists(xml_output_path):
        logger.info(f"The XML file already exists: {xml_output_path}.")
    else:
        logger.info(f"XML file not found. Creating the XML: {xml_output_path}")
        csv_to_xml_with_coordinates(csv_file_path, xml_output_path)

    # Verificar se o XSD já existe
    if os.path.exists(xsd_output_path):
        logger.info(f"XSD file already exists: {xsd_output_path}.")
    else:
        logger.info(f"XSD file not found. Creating the XSD: {xsd_output_path}")
        try:
            generate_xsd_from_xml(xml_output_path, xsd_output_path)
        except Exception as e:
            logger.error(f"Error creating XSD file: {e}", exc_info=True)

    # Validar o XML
    try:
        is_valid = validate_xml(xml_output_path, xsd_output_path)
        if is_valid:
            logger.info("XML is valid against XSD.")
        else:
            logger.warning("XML is not valid against XSD.")
    except Exception as e:
        logger.error(f"Error validating XML against XSD: {e}", exc_info=True)

    # Consulta XPath
    country_name = "USA"  # Substitua pelo nome do país que deseja buscar
    print(f"Fetching states of country {country_name} in XML...")
    states = get_states_by_country(xml_output_path, country_name)
    print(f"States found: {states}")

