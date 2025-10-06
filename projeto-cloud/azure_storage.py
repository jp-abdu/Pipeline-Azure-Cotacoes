from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

def save_file_to_blob(file_name, file_path):
    load_dotenv()

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("Azure Storage connection string não configurada")

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client("stocks")

        with open(file_path, "rb") as data:
            container_client.upload_blob(name=file_name, data=data, overwrite=True)

    except Exception as e:
        raise Exception(f"Erro ao salvar no Blob Storage: {str(e)}")

def get_file_from_blob(file_name):
    load_dotenv()

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("Azure Storage connection string não configurada")

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client("stocks")

        blob_client = container_client.get_blob_client(file_name)

        try:
            download_stream = blob_client.download_blob()
            blob_content = download_stream.readall().decode("utf-8")
            return blob_content
        except Exception as e:
            print("Error ao obter arquivo")
    except Exception as e:
        print("Error ao obter arquivo")



