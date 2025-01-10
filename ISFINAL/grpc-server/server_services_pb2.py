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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15server_services.proto\x12\x0fserver_services\"A\n\x16\x43onvertCSVToXMLRequest\x12\x11\n\tfile_name\x18\x01 \x01(\t\x12\x14\n\x0c\x66ile_content\x18\x02 \x01(\x0c\"A\n\x17\x43onvertCSVToXMLResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rxml_file_path\x18\x02 \x01(\t\"I\n\x13SendFileRequestBody\x12\x0c\n\x04\x66ile\x18\x01 \x01(\x0c\x12\x11\n\tfile_mime\x18\x02 \x01(\t\x12\x11\n\tfile_name\x18\x03 \x01(\t\"\'\n\x14SendFileResponseBody\x12\x0f\n\x07success\x18\x01 \x01(\x08\"8\n\x15SendFileChunksRequest\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\x12\x11\n\tfile_name\x18\x02 \x01(\t\":\n\x16SendFileChunksResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"\x1a\n\nCSVRequest\x12\x0c\n\x04\x66ile\x18\x01 \x01(\x0c\"Z\n\x13\x43oordinatesResponse\x12\x30\n\x0b\x63oordinates\x18\x01 \x03(\x0b\x32\x1b.server_services.Coordinate\x12\x11\n\tvalid_xml\x18\x02 \x01(\x08\"1\n\nCoordinate\x12\x11\n\tlongitude\x18\x01 \x01(\t\x12\x10\n\x08latitude\x18\x02 \x01(\t\"!\n\x0e\x43ountryRequest\x12\x0f\n\x07\x63ountry\x18\x01 \x01(\t\" \n\x0eStatesResponse\x12\x0e\n\x06states\x18\x01 \x03(\t2\xcf\x01\n\x0fSendFileService\x12W\n\x08SendFile\x12$.server_services.SendFileRequestBody\x1a%.server_services.SendFileResponseBody\x12\x63\n\x0eSendFileChunks\x12&.server_services.SendFileChunksRequest\x1a\'.server_services.SendFileChunksResponse(\x01\x32\x9c\x02\n\x0b\x46ileService\x12O\n\nProcessCSV\x12\x1b.server_services.CSVRequest\x1a$.server_services.CoordinatesResponse\x12V\n\x12GetStatesByCountry\x12\x1f.server_services.CountryRequest\x1a\x1f.server_services.StatesResponse\x12\x64\n\x0f\x43onvertCSVToXML\x12\'.server_services.ConvertCSVToXMLRequest\x1a(.server_services.ConvertCSVToXMLResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'server_services_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CONVERTCSVTOXMLREQUEST']._serialized_start=42
  _globals['_CONVERTCSVTOXMLREQUEST']._serialized_end=107
  _globals['_CONVERTCSVTOXMLRESPONSE']._serialized_start=109
  _globals['_CONVERTCSVTOXMLRESPONSE']._serialized_end=174
  _globals['_SENDFILEREQUESTBODY']._serialized_start=176
  _globals['_SENDFILEREQUESTBODY']._serialized_end=249
  _globals['_SENDFILERESPONSEBODY']._serialized_start=251
  _globals['_SENDFILERESPONSEBODY']._serialized_end=290
  _globals['_SENDFILECHUNKSREQUEST']._serialized_start=292
  _globals['_SENDFILECHUNKSREQUEST']._serialized_end=348
  _globals['_SENDFILECHUNKSRESPONSE']._serialized_start=350
  _globals['_SENDFILECHUNKSRESPONSE']._serialized_end=408
  _globals['_CSVREQUEST']._serialized_start=410
  _globals['_CSVREQUEST']._serialized_end=436
  _globals['_COORDINATESRESPONSE']._serialized_start=438
  _globals['_COORDINATESRESPONSE']._serialized_end=528
  _globals['_COORDINATE']._serialized_start=530
  _globals['_COORDINATE']._serialized_end=579
  _globals['_COUNTRYREQUEST']._serialized_start=581
  _globals['_COUNTRYREQUEST']._serialized_end=614
  _globals['_STATESRESPONSE']._serialized_start=616
  _globals['_STATESRESPONSE']._serialized_end=648
  _globals['_SENDFILESERVICE']._serialized_start=651
  _globals['_SENDFILESERVICE']._serialized_end=858
  _globals['_FILESERVICE']._serialized_start=861
  _globals['_FILESERVICE']._serialized_end=1145
# @@protoc_insertion_point(module_scope)
