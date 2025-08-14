from datetime import datetime
import requests
from helpers import yymmdd
import os
import zipfile

# Caminho relativo para salvar os dados dentro da pasta Script-Arquivos
PATH_TO_SAVE="./Script-Arquivos/dados_b3"

def build_url_download(date_to_download):
    # Adjust the URL format based on the B3 website's expected format
    # The current format might be incorrect, verify the correct URL pattern for B3 downloads
    return f"https://www.b3.com.br/pesquisapregao/download?filelist=PR{date_to_download}.zip"


def try_http_download(url: str):
    session = requests.Session()
    try:
        print(f"[INFO] Tentando {url}")
        resp = session.get(url, timeout=30)
        if (resp.ok) and resp.content and len(resp.content) > 200:
            if (resp.content[:2] == b"PK"):
                return resp.content, os.path.basename(url)
        print(f"[ERROR] Conteúdo da resposta inválido para {url}")
        return None, None
    except requests.RequestException:
        print(f"[ERROR] Erro ao acessar {url}")
        return None, None

def run():
    dt = yymmdd(datetime.now())
    url_to_download = build_url_download(dt)

    #1-Download do zip

    zip_bytes, zip_name = try_http_download(url_to_download)

    if not zip_bytes:
        raise RuntimeError("Não foi possível baixar o arquivo de cotações")
    
    print(f"[OK] Download do arquivo de cotações realizado com sucesso {zip_name}")

    #2-Salvar o zip

    #cria o diretorio que ira salvar o arquivo zip do download
    os.makedirs(PATH_TO_SAVE, exist_ok=True)

    zip_path = f"{PATH_TO_SAVE}/pregao_{dt}.zip"
    with open(zip_path, "wb") as file:
        file.write(zip_bytes)

    print(f"[OK] Arquivo de cotações salvo com sucesso em {zip_path}")

    #3-Extrair os arquivos do zip

    # Criar diretórios para extração dentro da pasta Script-Arquivos
    extract_dir1 = f"./Script-Arquivos/pregao_{dt}"
    extract_dir2 = f"./Script-Arquivos/PR{dt}"
    
    os.makedirs(extract_dir1, exist_ok=True)
    
    #Extrair a primeira pasta
    with zipfile.ZipFile(zip_path, "r") as zip_f:
        zip_f.extractall(extract_dir1)

    #Extrair a segunda pasta
    with zipfile.ZipFile(f"{extract_dir1}/PR{dt}.zip", "r") as zip_f:
        zip_f.extractall(extract_dir2)

    print(f"[OK] Arquivos de cotações extraidos do zip com sucesso")

if __name__ == "__main__":
    run()