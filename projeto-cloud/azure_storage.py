from azure.storage.blob import BlobServiceClient
from azure.storage.blob import PublicAccess
import os
import time

AZURE_BLOB_CONNECTION = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1;"
CONTAINER = "dados-pregao-bolsa"

def save_file_to_blob(file_name, local_path_file):
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"[INFO] Tentativa {attempt + 1} de {max_retries} para upload...")
            
            service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION)
            container = service.get_container_client(CONTAINER)
            
            # Ensure container exists
            try:
                service.create_container(CONTAINER, public_access=PublicAccess.Container)
                print(f"[INFO] Container '{CONTAINER}' criado.")
            except Exception as e:
                if "ContainerAlreadyExists" in str(e):
                    print(f"[INFO] Container '{CONTAINER}' já existe.")
                else:
                    print(f"[WARN] Erro ao criar container: {e}")

            # Check file size and properties
            file_size = os.path.getsize(local_path_file)
            print(f"[INFO] Tamanho do arquivo: {file_size} bytes")

            with open(local_path_file, "rb") as data:
                print(f"[INFO] Fazendo upload de '{file_name}' para o container '{CONTAINER}'...")
                
                # Upload with basic parameters only for compatibility
                container.upload_blob(
                    name=file_name, 
                    data=data, 
                    overwrite=True
                )
                print(f"[SUCCESS] Upload de '{file_name}' concluído.")
                return  # Success, exit function
                
        except Exception as e:
            print(f"[ERROR] Tentativa {attempt + 1} falhou: {type(e).__name__}: {e}")
            print(f"[ERROR] Arquivo: {file_name}, Caminho: {local_path_file}")
            
            if attempt < max_retries - 1:
                print(f"[INFO] Aguardando {retry_delay} segundos antes da próxima tentativa...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"[ERROR] Todas as {max_retries} tentativas falharam. Desistindo.")
                raise

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