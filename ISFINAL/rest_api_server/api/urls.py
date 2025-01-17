from django.urls import path
from api.views.file_views import FileUploadView, FileUploadChunksView
from .views.users import GetAllUsers
from .views.convert_csv_to_xml_view import ConvertCSVToXMLView
from .views.convert_xml_to_xsd_view import ConvertXMLToXSDView
from .views.get_states_by_country import GetStatesByCountryView
from .views.import_xml_view import export_xml_to_db

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload-file'),
    path('upload-file/by-chunks/', FileUploadChunksView.as_view(), name='upload-file-by-chunks'),
    path('users/', GetAllUsers.as_view(), name='users'),
    path('convert-csv-to-xml/', ConvertCSVToXMLView.as_view(), name='convert_csv_to_xml'),
    path('convert-xml-to-xsd/', ConvertXMLToXSDView.as_view(), name='convert_xml_to_xsd'),
    path('get-states-by-country/', GetStatesByCountryView.as_view(), name='get_states_by_country'),
    path('export-xml-to-db/', export_xml_to_db, name='export-xml-to-db'),
]
