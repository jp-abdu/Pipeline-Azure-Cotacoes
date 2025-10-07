from azure.storage.blob import BlobServiceClient
from azure.storage.blob import PublicAccess

AZURE_BLOB_CONNECTION = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1;"
CONTAINER = "dados-pregao-bolsa"

def save_file_to_blob(file_name, local_path_file):
    service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION)
    container = service.get_container_client(CONTAINER)
    try:
        service.create_container(CONTAINER, public_access=PublicAccess.Container)
    except Exception as e:
        if "ContainerAlreadyExists" not in str(e):
            print(f"[WARN] Erro ao criar container, mas não é 'AlreadyExists': {e}")

    with open(local_path_file, "rb") as data:
        print(f"[INFO] Fazendo upload de '{file_name}' para o container '{CONTAINER}'...")
        container.upload_blob(name=file_name, data=data, overwrite=True)
        print(f"[SUCCESS] Upload de '{file_name}' concluído.")

def get_file_from_blob(file_name):
    service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION)
    container = service.get_container_client(CONTAINER)

    blob_client = container.get_blob_client(file_name)

    try:
        print(f"[INFO] Lendo o blob '{file_name}' do Blob Storage...")
        download_stream = blob_client.download_blob()
        blob_content = download_stream.readall().decode("utf-8")
        print(f"[SUCCESS] Leitura do blob '{file_name}' concluída.")
        return blob_content
    except Exception as e:
        print(f"[ERROR] Erro ao obter arquivo '{file_name}' do blob: {e}")
        raise