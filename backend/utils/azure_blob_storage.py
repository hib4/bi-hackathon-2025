import base64
from settings import settings
from azure.storage.blob import BlobClient

STORAGE_ACCOUNT_NAME = "bihackathon"
CONTAINER_NAME = "storage"
SAS_TOKEN = settings.MICROSOFT_AZURE_BLOB_SAS_TOKEN

def upload_file_to_blob(base64_string: str, folder_name: str,blob_filename: str) -> str:
    blob_path = f"{folder_name}/{blob_filename}"
    blob_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{blob_path}?{SAS_TOKEN}"

    blob_client = BlobClient.from_blob_url(blob_url)
    file_bytes = base64.b64decode(base64_string)
    blob_client.upload_blob(file_bytes, overwrite=True)

    uploaded_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{blob_path}"
    return uploaded_url
