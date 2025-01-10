from django.urls import path
from api.views.file_views import FileUploadView, FileUploadChunksView
from .views.users import GetAllUsers
from .views.convert_csv_to_xml_view import ConvertCSVToXMLView

urlpatterns = [
path('upload-file/', FileUploadView.as_view(), name='uploadfile'),
path('upload-file/by-chunks', FileUploadChunksView.as_view(),
name='upload-file-by-chunks'),
path('users/', GetAllUsers.as_view(), name='users'),
path('convert-csv-to-xml/', ConvertCSVToXMLView.as_view(), name='convert_csv_to_xml'),
]
