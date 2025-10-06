from datetime import datetime, timedelta
from helpers import yymmdd
import requests
import os
import zipfile
from azure_storage import save_file_to_blob
import shutil
from process_stocks import StockProcessor
from dotenv import load_dotenv # ADICIONE ESTA IMPORTAÇÃO

load_dotenv() # ADICIONE ESTA LINHA AQUI, LOGO APÓS AS IMPORTAÇÕES

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
    # Retorna None se qualquer condição falhar
    return None

def run():
    # 1) Tenta baixar o arquivo de hoje
    today = datetime.now()
    dt_str = yymmdd(today)
    url_to_download = build_url_download(dt_str)
    download_result = try_http_download(url_to_download)

    # 2) Failsafe: se falhar, busca o último dia útil disponível
    if not download_result:
        print(f"[WARN] Não foi possível baixar o arquivo para a data de hoje ({dt_str}). Buscando o último dia útil...")
        # Loop para voltar nos últimos 7 dias
        for i in range(1, 8):
            previous_date = today - timedelta(days=i)
            # Verifica se é um dia de semana (Segunda=0, Sexta=4)
            if previous_date.weekday() < 5:
                dt_str = yymmdd(previous_date)
                url_to_download = build_url_download(dt_str)
                download_result = try_http_download(url_to_download)
                # Se o download for bem-sucedido, para a busca
                if download_result:
                    break

    # Se não encontrou nenhum arquivo nos últimos 7 dias, encerra o programa
    if not download_result:
        raise RuntimeError("Não foi possível baixar o arquivo de cotações nos últimos 7 dias.")

    # Extrai os dados do download bem-sucedido
    zip_bytes, zip_name = download_result
    # Converte a string da data (que pode ser de hoje ou de um dia anterior) para um objeto datetime
    dt_obj = datetime.strptime(dt_str, "%y%m%d").date()
    print(f"[OK] Baixado arquivo de cotações para a data {dt_obj}: {zip_name}")

    try:
        # Salvar o Zip
        os.makedirs(PATH_TO_SAVE, exist_ok=True)
        zip_path = f"{PATH_TO_SAVE}/pregao_{dt_str}.zip"
        with open(zip_path, "wb") as f:
            f.write(zip_bytes)
        print(f"[OK] Zip salvo em {zip_path}")

        # Extrair os arquivos do zip
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(f"{PATH_TO_SAVE}/pregao_{dt_str}")

        with zipfile.ZipFile(f"{PATH_TO_SAVE}/pregao_{dt_str}/SPRE{dt_str}.zip", "r") as zf:
            zf.extractall(f"{PATH_TO_SAVE}/SPRE{dt_str}")

        # Processar arquivos
        arquivos = [f for f in os.listdir(f"{PATH_TO_SAVE}/SPRE{dt_str}")]
        processor = StockProcessor()

        for arquivo in arquivos:
            file_path = f"{PATH_TO_SAVE}/SPRE{dt_str}/{arquivo}"

            try:
                save_file_to_blob(f"BVBG186_{dt_str}.xml", file_path)
                print(f"[OK] Arquivo salvo no Blob Storage: BVBG186_{dt_str}.xml")
            except Exception as e:
                print(f"[WARN] Não foi possível salvar no Blob Storage: {str(e)}")

            processor.process_xml_file(file_path, fallback_date=dt_obj)

    finally:
        try:
            shutil.rmtree(f"{PATH_TO_SAVE}", ignore_errors=True)
            print("[OK] Arquivos temporários removidos")
        except Exception as e:
            print(f"[WARN] Erro ao limpar arquivos temporários: {str(e)}")

    print(f"[OK] Processamento finalizado")


if __name__ == "__main__":
    run()