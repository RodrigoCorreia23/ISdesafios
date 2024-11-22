import xml.etree.ElementTree as ET
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def parse_xml(file_path):
    "Parse and validate XML file, returning the root if successful."
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def validate_xml(element):
    "Validate XML by checking for necessary tags or structure, if needed."
    if element.tag is None:
        print("Invalid XML: No root tag found.")
        return False
    print("XML is valid.")
    return True

def print_content(element, level=0):
    "Recursively print XML content with tag names."
    if element.text and element.text.strip():
        indent = " " * (level * 2)
        print(f"{indent}{element.tag}: {element.text.strip()}")
    for child in element:
        print_content(child, level + 1)

if __name__ == "__main__":
    Tk().withdraw()
    file_path = askopenfilename(filetypes=[("XML files", "*.xml")], title="Select an XML file")
    
    if file_path:
        root = parse_xml(file_path)
        if root and validate_xml(root):
            print("XML Content:")
            print_content(root)
        else:
            print("The XML file is not valid.")
    else:
        print("No file selected.")
