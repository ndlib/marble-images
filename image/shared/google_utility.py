""" Common code to perform basic google drive calls """
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
import socket


def _get_credentials_from_service_account_info(credentials):
    """ Return credentials given service account file and assumptions of scopes needed """
    service_account_info = credentials
    # Scopes: https://developers.google.com/identity/protocols/googlescopes
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    return (credentials)


def establish_connection(credentials):
    """ Create a connection to the Google API """
    timeout_in_sec = 5  # timeout for build process
    socket.setdefaulttimeout(timeout_in_sec)
    credentials = _get_credentials_from_service_account_info(credentials)
    return build('drive', 'v3', credentials=credentials)


def download_file(connection, file_id, local_file_name) -> bool:
    downloaded = True
    try:
        request = connection.files().get_media(fileId=file_id)
        fh = io.FileIO(local_file_name, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    except socket.timeout as e:
        print(f"Error downloading {local_file_name} - {e}")
        downloaded = False
    return downloaded
