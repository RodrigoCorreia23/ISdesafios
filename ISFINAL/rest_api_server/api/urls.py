from django.urls import path
from .views.file_views import FileUploadView, FileUploadChunksView
from .views.get_info_by_cardinalpoint import GetInfoByCardinalPointView
from .views.users import GetAllUsers
from .views.convert_csv_to_xml_view import ConvertCSVToXMLView
from .views.convert_xml_to_xsd_view import ConvertXMLToXSDView
from .views.get_states_by_country import GetStatesByCountryView
from .views.import_xml_view import export_xml_to_db
from .views.warehouses import GetWarehousesView, UpdateWarehouseView, FilterByProductLineView
from .views.get_sales_by_country_and_year import GetSalesByCountryAndYearView

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload-file'),
    path('upload-file/by-chunks/', FileUploadChunksView.as_view(), name='upload-file-by-chunks'),
    path('users/', GetAllUsers.as_view(), name='users'),
    path('convert-csv-to-xml/', ConvertCSVToXMLView.as_view(), name='convert_csv_to_xml'),
    path('convert-xml-to-xsd/', ConvertXMLToXSDView.as_view(), name='convert_xml_to_xsd'),
    path('get-states-by-country/', GetStatesByCountryView.as_view(), name='get_states_by_country'),
    path('get-info-by-cardinalpoint/', GetInfoByCardinalPointView.as_view(), name='get_info_by_cardinalpoint'),
    path('export-xml-to-db/', export_xml_to_db, name='export-xml-to-db'),
    path('get-warehouses/', GetWarehousesView.as_view(), name='get-warehouses'),
    path('warehouses/<int:id>/', UpdateWarehouseView.as_view(), name='update-warehouse'),
    path('filter-by-productline/', FilterByProductLineView.as_view(), name='filter-by-productline'),
    path('sales/by-country-and-year/', GetSalesByCountryAndYearView.as_view(), name='get_sales_by_country_and_year'),
]
