from datetime import datetime
from helpers import yymmdd
import requests
import os
import zipfile
from azure_storage import save_file_to_blob
import shutil
from process_stocks import StockProcessor

PATH_TO_SAVE = "./dados_b3"

def build_url_download(date_to_download):
    return f"https://www.b3.com.br/pesquisapregao/download?filelist=SPRE{date_to_download}.zip"

def try_http_download(url):
    session = requests.Session()
    try:
        print(f"[INFO] Tentando {url}")
        resp = session.get(url, timeout=30)
        if (resp.ok) and resp.content and len(resp.content) > 200:
            if (resp.content[:2] == b"PK"):
                return resp.content, os.path.basename(url)
    except requests.RequestException:
        print(f"[ERROR] Falha ao acessar a {url}")
        pass

def run():
    dt_str = "250923" #yymmdd(datetime.now())
    # Converte a string da data para um objeto datetime
    dt_obj = datetime.strptime(dt_str, "%y%m%d").date()

    url_to_download = build_url_download(dt_str)

    # 1) Download do Zip
    zip_bytes, zip_name = try_http_download(url_to_download)

    if not zip_bytes:
        raise RuntimeError("Não foi possivel baixar o arquivo de cotações")

    print(f"[OK] Baixado arquivo de cotaçoes: {zip_name}")

    try:
        # 2) Salvar o Zip
        os.makedirs(PATH_TO_SAVE, exist_ok=True)
        zip_path = f"{PATH_TO_SAVE}/pregao_{dt_str}.zip"
        with open(zip_path, "wb") as f:
            f.write(zip_bytes)

        print(f"[OK] Zip salvo em {zip_path}")

        # 3) Extrair os arquivos do zip
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(f"{PATH_TO_SAVE}/pregao_{dt_str}")

        with zipfile.ZipFile(f"{PATH_TO_SAVE}/pregao_{dt_str}/SPRE{dt_str}.zip", "r") as zf:
            zf.extractall(f"{PATH_TO_SAVE}/SPRE{dt_str}")

        # Processar arquivos
        arquivos = [f for f in os.listdir(f"{PATH_TO_SAVE}/SPRE{dt_str}")]
        processor = StockProcessor()

        for arquivo in arquivos:
            file_path = f"{PATH_TO_SAVE}/SPRE{dt_str}/{arquivo}"

            # Tenta salvar no Blob Storage, mas continua mesmo se falhar
            try:
                save_file_to_blob(f"BVBG186_{dt_str}.xml", file_path)
                print(f"[OK] Arquivo salvo no Blob Storage: BVBG186_{dt_str}.xml")
            except Exception as e:
                print(f"[WARN] Não foi possível salvar no Blob Storage: {str(e)}")

            # Processa o arquivo XML e salva no PostgreSQL, passando a data como fallback
            processor.process_xml_file(file_path, fallback_date=dt_obj)

    finally:
        # Sempre tenta limpar os arquivos temporários
        try:
            shutil.rmtree(f"{PATH_TO_SAVE}", ignore_errors=True)
            print("[OK] Arquivos temporários removidos")
        except Exception as e:
            print(f"[WARN] Erro ao limpar arquivos temporários: {str(e)}")

    print(f"[OK] Processamento finalizado")


if __name__ == "__main__":
    run()