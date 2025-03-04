# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: server_services.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'server_services.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15server_services.proto\x12\x0fserver_services\"A\n\x16\x43onvertXMLToXSDRequest\x12\x11\n\tfile_name\x18\x01 \x01(\t\x12\x14\n\x0c\x66ile_content\x18\x02 \x01(\x0c\"A\n\x17\x43onvertXMLToXSDResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rxsd_file_path\x18\x02 \x01(\t\"A\n\x16\x43onvertCSVToXMLRequest\x12\x11\n\tfile_name\x18\x01 \x01(\t\x12\x14\n\x0c\x66ile_content\x18\x02 \x01(\x0c\"A\n\x17\x43onvertCSVToXMLResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rxml_file_path\x18\x02 \x01(\t\"I\n\x13SendFileRequestBody\x12\x0c\n\x04\x66ile\x18\x01 \x01(\x0c\x12\x11\n\tfile_mime\x18\x02 \x01(\t\x12\x11\n\tfile_name\x18\x03 \x01(\t\"\'\n\x14SendFileResponseBody\x12\x0f\n\x07success\x18\x01 \x01(\x08\"8\n\x15SendFileChunksRequest\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\x12\x11\n\tfile_name\x18\x02 \x01(\t\":\n\x16SendFileChunksResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"\x1a\n\nCSVRequest\x12\x0c\n\x04\x66ile\x18\x01 \x01(\x0c\"Z\n\x13\x43oordinatesResponse\x12\x30\n\x0b\x63oordinates\x18\x01 \x03(\x0b\x32\x1b.server_services.Coordinate\x12\x11\n\tvalid_xml\x18\x02 \x01(\x08\"1\n\nCoordinate\x12\x11\n\tlongitude\x18\x01 \x01(\t\x12\x10\n\x08latitude\x18\x02 \x01(\t\"!\n\x0e\x43ountryRequest\x12\x0f\n\x07\x63ountry\x18\x01 \x01(\t\"B\n\x0f\x43ountryResponse\x12/\n\x0bsales_items\x18\x01 \x03(\x0b\x32\x1a.server_services.SalesItem\" \n\x0eStatesResponse\x12\x0e\n\x06states\x18\x01 \x03(\t\" \n\rStatesRequest\x12\x0f\n\x07\x63ountry\x18\x01 \x01(\t\"\xae\x02\n\x15\x43\x61rdinalPointResponse\x12G\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x39.server_services.CardinalPointResponse.CardinalPointEntry\x1a\xcb\x01\n\x12\x43\x61rdinalPointEntry\x12\x0c\n\x04\x64\x61te\x18\x01 \x01(\t\x12\x11\n\twarehouse\x18\x02 \x01(\t\x12\x13\n\x0b\x63lient_type\x18\x03 \x01(\t\x12\x14\n\x0cproduct_line\x18\x04 \x01(\t\x12\x10\n\x08quantity\x18\x05 \x01(\x05\x12\x12\n\nunit_price\x18\x06 \x01(\x02\x12\r\n\x05total\x18\x07 \x01(\x02\x12\x0f\n\x07payment\x18\x08 \x01(\t\x12\x10\n\x08latitude\x18\t \x01(\x02\x12\x11\n\tlongitude\x18\n \x01(\x02\")\n\x14\x43\x61rdinalPointRequest\x12\x11\n\twarehouse\x18\x01 \x01(\t\"F\n\x1b\x43onvertXMLToDatabaseRequest\x12\x11\n\tfile_name\x18\x01 \x01(\t\x12\x14\n\x0c\x66ile_content\x18\x02 \x01(\x0c\"3\n\x0fGenericResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\",\n\x17\x45xportToDatabaseRequest\x12\x11\n\tfile_name\x18\x01 \x01(\t\"<\n\x18\x45xportToDatabaseResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"A\n\tSalesItem\x12\x0f\n\x07\x63ountry\x18\x01 \x01(\t\x12\x11\n\tlongitude\x18\x02 \x01(\x02\x12\x10\n\x08latitude\x18\x03 \x01(\x02\"-\n\x0cSalesRequest\x12\x0f\n\x07\x63ountry\x18\x01 \x01(\t\x12\x0c\n\x04year\x18\x02 \x01(\t\"&\n\x04Sale\x12\r\n\x05state\x18\x01 \x01(\t\x12\x0f\n\x07revenue\x18\x02 \x01(\x02\"5\n\rSalesResponse\x12$\n\x05sales\x18\x01 \x03(\x0b\x32\x15.server_services.Sale2\xd6\x07\n\x0b\x46ileService\x12\x63\n\x0eSendFileChunks\x12&.server_services.SendFileChunksRequest\x1a\'.server_services.SendFileChunksResponse(\x01\x12O\n\nProcessCSV\x12\x1b.server_services.CSVRequest\x1a$.server_services.CoordinatesResponse\x12V\n\x12GetStatesByCountry\x12\x1f.server_services.CountryRequest\x1a\x1f.server_services.StatesResponse\x12g\n\x16GetInfoByCardinalPoint\x12%.server_services.CardinalPointRequest\x1a&.server_services.CardinalPointResponse\x12\x64\n\x0f\x43onvertCSVToXML\x12\'.server_services.ConvertCSVToXMLRequest\x1a(.server_services.ConvertCSVToXMLResponse\x12\x64\n\x0f\x43onvertXMLToXSD\x12\'.server_services.ConvertXMLToXSDRequest\x1a(.server_services.ConvertXMLToXSDResponse\x12\x66\n\x14\x43onvertXMLToDatabase\x12,.server_services.ConvertXMLToDatabaseRequest\x1a .server_services.GenericResponse\x12g\n\x10\x45xportToDatabase\x12(.server_services.ExportToDatabaseRequest\x1a).server_services.ExportToDatabaseResponse\x12X\n\x13GetCountryLocations\x12\x1f.server_services.CountryRequest\x1a .server_services.CountryResponse\x12Y\n\x18GetSalesByCountryAndYear\x12\x1d.server_services.SalesRequest\x1a\x1e.server_services.SalesResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'server_services_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CONVERTXMLTOXSDREQUEST']._serialized_start=42
  _globals['_CONVERTXMLTOXSDREQUEST']._serialized_end=107
  _globals['_CONVERTXMLTOXSDRESPONSE']._serialized_start=109
  _globals['_CONVERTXMLTOXSDRESPONSE']._serialized_end=174
  _globals['_CONVERTCSVTOXMLREQUEST']._serialized_start=176
  _globals['_CONVERTCSVTOXMLREQUEST']._serialized_end=241
  _globals['_CONVERTCSVTOXMLRESPONSE']._serialized_start=243
  _globals['_CONVERTCSVTOXMLRESPONSE']._serialized_end=308
  _globals['_SENDFILEREQUESTBODY']._serialized_start=310
  _globals['_SENDFILEREQUESTBODY']._serialized_end=383
  _globals['_SENDFILERESPONSEBODY']._serialized_start=385
  _globals['_SENDFILERESPONSEBODY']._serialized_end=424
  _globals['_SENDFILECHUNKSREQUEST']._serialized_start=426
  _globals['_SENDFILECHUNKSREQUEST']._serialized_end=482
  _globals['_SENDFILECHUNKSRESPONSE']._serialized_start=484
  _globals['_SENDFILECHUNKSRESPONSE']._serialized_end=542
  _globals['_CSVREQUEST']._serialized_start=544
  _globals['_CSVREQUEST']._serialized_end=570
  _globals['_COORDINATESRESPONSE']._serialized_start=572
  _globals['_COORDINATESRESPONSE']._serialized_end=662
  _globals['_COORDINATE']._serialized_start=664
  _globals['_COORDINATE']._serialized_end=713
  _globals['_COUNTRYREQUEST']._serialized_start=715
  _globals['_COUNTRYREQUEST']._serialized_end=748
  _globals['_COUNTRYRESPONSE']._serialized_start=750
  _globals['_COUNTRYRESPONSE']._serialized_end=816
  _globals['_STATESRESPONSE']._serialized_start=818
  _globals['_STATESRESPONSE']._serialized_end=850
  _globals['_STATESREQUEST']._serialized_start=852
  _globals['_STATESREQUEST']._serialized_end=884
  _globals['_CARDINALPOINTRESPONSE']._serialized_start=887
  _globals['_CARDINALPOINTRESPONSE']._serialized_end=1189
  _globals['_CARDINALPOINTRESPONSE_CARDINALPOINTENTRY']._serialized_start=986
  _globals['_CARDINALPOINTRESPONSE_CARDINALPOINTENTRY']._serialized_end=1189
  _globals['_CARDINALPOINTREQUEST']._serialized_start=1191
  _globals['_CARDINALPOINTREQUEST']._serialized_end=1232
  _globals['_CONVERTXMLTODATABASEREQUEST']._serialized_start=1234
  _globals['_CONVERTXMLTODATABASEREQUEST']._serialized_end=1304
  _globals['_GENERICRESPONSE']._serialized_start=1306
  _globals['_GENERICRESPONSE']._serialized_end=1357
  _globals['_EXPORTTODATABASEREQUEST']._serialized_start=1359
  _globals['_EXPORTTODATABASEREQUEST']._serialized_end=1403
  _globals['_EXPORTTODATABASERESPONSE']._serialized_start=1405
  _globals['_EXPORTTODATABASERESPONSE']._serialized_end=1465
  _globals['_SALESITEM']._serialized_start=1467
  _globals['_SALESITEM']._serialized_end=1532
  _globals['_SALESREQUEST']._serialized_start=1534
  _globals['_SALESREQUEST']._serialized_end=1579
  _globals['_SALE']._serialized_start=1581
  _globals['_SALE']._serialized_end=1619
  _globals['_SALESRESPONSE']._serialized_start=1621
  _globals['_SALESRESPONSE']._serialized_end=1674
  _globals['_FILESERVICE']._serialized_start=1677
  _globals['_FILESERVICE']._serialized_end=2659
# @@protoc_insertion_point(module_scope)
