import csv
import os
import lxml.etree as etree
import argparse
import sys

# Selecionar ficheiro CSV via argumento de linha de comando
def selecionar_ficheiro_csv():
    parser = argparse.ArgumentParser(description="Processar um arquivo CSV.")
    parser.add_argument('--file', required=True, help="Caminho para o arquivo CSV.")
    args = parser.parse_args()
    if not os.path.exists(args.file):
        print("O ficheiro especificado não existe.")
        exit(1)
    return args.file

# Converter CSV para XML
def csv_para_xml(ficheiro_csv, nome_xml):
    root = etree.Element("root")
    
    with open(ficheiro_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            item = etree.SubElement(root, "item")
            for key, value in row.items():
                child = etree.SubElement(item, key)
                child.text = value
    
    tree = etree.ElementTree(root)
    tree.write(nome_xml, encoding="utf-8", xml_declaration=True, pretty_print=True)

# Gerar XSD simples a partir do XML
def gerar_xsd_simples(nome_xml, nome_xsd):
    tree = etree.parse(nome_xml)
    root = tree.getroot()

    XS_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
    schema_root = etree.Element("{%s}schema" % XS_NAMESPACE, 
                                nsmap={'xs': XS_NAMESPACE}, 
                                elementFormDefault="qualified")

    element_root = etree.SubElement(schema_root, "{%s}element" % XS_NAMESPACE, name="root")
    complex_type_root = etree.SubElement(element_root, "{%s}complexType" % XS_NAMESPACE)
    sequence_root = etree.SubElement(complex_type_root, "{%s}sequence" % XS_NAMESPACE)

    element_item = etree.SubElement(sequence_root, "{%s}element" % XS_NAMESPACE, name="item", maxOccurs="unbounded")
    complex_type_item = etree.SubElement(element_item, "{%s}complexType" % XS_NAMESPACE)
    sequence_item = etree.SubElement(complex_type_item, "{%s}sequence" % XS_NAMESPACE)

    first_item = root.find("item")
    if first_item is not None:
        for child in first_item:
            etree.SubElement(sequence_item, "{%s}element" % XS_NAMESPACE, name=child.tag, type="xs:string")

    xsd_tree = etree.ElementTree(schema_root)
    xsd_tree.write(nome_xsd, encoding="utf-8", xml_declaration=True, pretty_print=True)

# Validar XML com o XSD
def validar_xml(nome_xml, nome_xsd):
    try:
        xmlschema_doc = etree.parse(nome_xsd)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        
        xml_doc = etree.parse(nome_xml)
        is_valid = xmlschema.validate(xml_doc)
        
        if not is_valid:
            for error in xmlschema.error_log:
                print(f"Erro de validação: {error.message} na linha {error.line}.")
        return is_valid
    except etree.XMLSchemaParseError as e:
        print(f"Erro ao carregar o XSD: {e}")
        return False
    except etree.XMLSyntaxError as e:
        print(f"Erro de sintaxe no XML: {e}")
        return False
    except Exception as e:
        print(f"Ocorreu um erro durante a validação: {e}")
        return False

# Criar Sub-XML filtrado por categoria
def criar_sub_xml(nome_xml, nome_sub_xml, tag, valor):
    tree = etree.parse(nome_xml)
    root = tree.getroot()
    
    sub_root = etree.Element("root")
    
    for item in root.findall("item"):
        if item.find(tag) is not None and item.find(tag).text == valor:
            sub_root.append(item)
    
    sub_tree = etree.ElementTree(sub_root)
    sub_tree.write(nome_sub_xml, encoding="utf-8", xml_declaration=True, pretty_print=True)

# Explorar Sub-XML com XPath
def explorar_com_xpath(nome_xml, xpath_expr):
    tree = etree.parse(nome_xml)
    results = tree.xpath(xpath_expr)
    return results

def main():
    if len(sys.argv) < 2:
        print("Erro: Por favor, forneça o caminho do arquivo CSV.")
        return

    ficheiro_csv = sys.argv[1]

    if not os.path.isfile(ficheiro_csv):
        print(f"Erro: O arquivo {ficheiro_csv} não foi encontrado.")
        return

    # Converter CSV para XML
    nome_xml = os.path.splitext(ficheiro_csv)[0] + ".xml"
    csv_para_xml(ficheiro_csv, nome_xml)
    print(f"Ficheiro XML '{nome_xml}' gerado a partir do CSV.")

    # Gerar XSD
    nome_xsd = "schema.xsd"
    gerar_xsd_simples(nome_xml, nome_xsd)
    print(f"Ficheiro XSD '{nome_xsd}' gerado com base no XML.")

    # Validar XML
    if validar_xml(nome_xml, nome_xsd):
        print("O XML é válido segundo o XSD gerado.")
    else:
        print("O XML NÃO é válido segundo o XSD gerado.")
        return

    # Verificar se os argumentos para categoria e valor foram fornecidos
    if len(sys.argv) < 4:
        print("Erro: Por favor, forneça o nome da categoria e o valor.")
        return

    tag_categoria = sys.argv[2]
    valor_categoria = sys.argv[3]

    # Criar Sub-XML filtrado
    nome_sub_xml = "SUB-" + os.path.splitext(os.path.basename(ficheiro_csv))[0] + ".xml"
    criar_sub_xml(nome_xml, nome_sub_xml, tag_categoria, valor_categoria)
    print(f"Sub-XML '{nome_sub_xml}' criado com base na categoria '{tag_categoria}' e valor '{valor_categoria}'.")

if __name__ == "__main__":
    main()