""" Common code to perform basic google drive calls """
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import Error
import io
import socket
from . import logger


def establish_connection(credentials):
    """ Create a connection to the Google API """
    socket.setdefaulttimeout(5)  # timeout in seconds for build process
    scopes = ['https://www.googleapis.com/auth/drive']
    google_creds = service_account.Credentials.from_service_account_info(credentials, scopes=scopes)
    return build('drive', 'v3', credentials=google_creds)


def download_file(connection, file_id, local_file_name) -> bool:
    downloaded = True
    try:
        request = connection.files().get_media(fileId=file_id)
        fh = io.FileIO(local_file_name, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    except Error as e:
        logger.error(f"Error downloading {file_id} to {local_file_name} - {e}")
        downloaded = False
    except socket.timeout as e:
        logger.error(f"Error downloading {file_id} to {local_file_name} - {e}")
        downloaded = False
    return downloaded
