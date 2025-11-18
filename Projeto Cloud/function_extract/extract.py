from datetime import datetime, timedelta
from helpers import yymmdd
import requests
import os
import zipfile
from azure_storage import save_file_to_blob
import shutil
import logging

#Permite salvar os arquivos temporarios na pasta TEMP do sistema operacional
PATH_TO_SAVE = '/tmp/dados_b3'

if not os.path.exists(PATH_TO_SAVE):
    os.makedirs(PATH_TO_SAVE)
    msg = f"Pasta criada: {PATH_TO_SAVE}"
    logging.info(msg)
else:
    msg = f"Pasta já existe: {PATH_TO_SAVE}"
    logging.info(msg)

def build_url_download(date_to_download):
    return f"https://www.b3.com.br/pesquisapregao/download?filelist=SPRE{date_to_download}.zip"

def try_http_download(url):
    session = requests.Session()
    try:
        logging.info(f"[INFO] Tentando {url}")
        resp = session.get(url, timeout=30)
        if (resp.ok) and resp.content:
            if (resp.content[:2] == b"PK"):
                return resp.content, os.path.basename(url)
    except requests.RequestException:
        logging.error(f"[ERROR] Falha ao acessar a {url}")
        pass

def run():
    # Tenta baixar o arquivo dos últimos 7 dias (para cobrir finais de semana e feriados)
    max_attempts = 7
    zip_bytes = None
    zip_name = None
    dt = None

    for days_back in range(max_attempts):
        target_date = datetime.now() - timedelta(days=days_back)
        dt = yymmdd(target_date)
        url_to_download = build_url_download(dt)

        # 1) Tentativa de Download do Zip
        result = try_http_download(url_to_download)

        if result:
            zip_bytes, zip_name = result
            logging.info(f"[OK] Arquivo encontrado para {target_date.strftime('%d/%m/%Y')}")
            logging.info(f"[OK] Baixado arquivo de cotações: {zip_name}")
            break
        else:
            logging.info(f"[INFO] Arquivo não encontrado para {target_date.strftime('%d/%m/%Y')}, tentando dia anterior...")

    if not zip_bytes:
        raise RuntimeError(f"Não foi possível baixar o arquivo de cotações dos últimos {max_attempts} dias")

    # 2) Salvar o Zip

    #Cria o diretorio que ira salvar o arquivo zip do download
    os.makedirs(PATH_TO_SAVE, exist_ok=True)
    zip_path = f"{PATH_TO_SAVE}/pregao_{dt}.zip"
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    logging.info(f"[OK] Zip salvo em {zip_path}")

    # 3) Extrair os arquivos do zip

    #Extrair a primeira pasta
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(f"{PATH_TO_SAVE}/pregao_{dt}")


    #Extrair a segunda parte
    with zipfile.ZipFile(f"{PATH_TO_SAVE}/pregao_{dt}/SPRE{dt}.zip", "r") as zf:
        zf.extractall(f"{PATH_TO_SAVE}/pregao_{dt}/SPRE{dt}")


    #Subir arquivo para o Blob Storage
    arquivos = [f for f in os.listdir(f"{PATH_TO_SAVE}/pregao_{dt}/SPRE{dt}")]

    for arquivo in arquivos:
        save_file_to_blob(f"BVBG186_{dt}.xml", f"{PATH_TO_SAVE}/pregao_{dt}/SPRE{dt}/{arquivo}")

    #Apagar arquivos desnecessários
    shutil.rmtree(f"{PATH_TO_SAVE}/pregao_{dt}", ignore_errors=True)

    logging.info(f"[OK] Arquivos extraidos do zip com sucesso")


if __name__ == "__main__":
    run()