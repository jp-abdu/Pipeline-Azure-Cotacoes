from datetime import datetime, timedelta
from helpers import yymmdd
import requests
import os
import zipfile
import io
import tempfile
from azure_storage import save_file_to_blob, get_file_from_blob
from process_stocks import StockProcessor
from dotenv import load_dotenv

load_dotenv()

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
    return None

def run():
    today = datetime.now()
    dt_str = yymmdd(today)
    url_to_download = build_url_download(dt_str)
    download_result = try_http_download(url_to_download)

    if not download_result:
        print(f"[WARN] Não foi possível baixar o arquivo para a data de hoje ({dt_str}). Buscando o último dia útil...")
        for i in range(1, 8):
            previous_date = today - timedelta(days=i)
            if previous_date.weekday() < 5:
                dt_str = yymmdd(previous_date)
                url_to_download = build_url_download(dt_str)
                download_result = try_http_download(url_to_download)
                if download_result:
                    break

    if not download_result:
        raise RuntimeError("Não foi possível baixar o arquivo de cotações nos últimos 7 dias.")

    zip_bytes, zip_name = download_result
    dt_obj = datetime.strptime(dt_str, "%y%m%d").date()
    print(f"[OK] Baixado arquivo de cotações para a data {dt_obj}: {zip_name}")

    xml_bytes = None
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf1:
        nested_zip_name = f"SPRE{dt_str}.zip"
        nested_zip_bytes = zf1.read(nested_zip_name)
        with zipfile.ZipFile(io.BytesIO(nested_zip_bytes), "r") as zf2:
            for name in zf2.namelist():
                if name.endswith('.xml'):
                    xml_bytes = zf2.read(name)
                    break

    if not xml_bytes:
        raise RuntimeError("Não foi possível encontrar o arquivo XML dentro dos arquivos ZIP.")

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml", mode='wb') as temp_f:
            temp_f.write(xml_bytes)
            temp_file_path = temp_f.name

        print(f"[INFO] XML extraído para arquivo temporário: {temp_file_path}")

        blob_name = f"BVBG186_{dt_str}.xml"
        save_file_to_blob(blob_name, temp_file_path)

        xml_string_from_blob = get_file_from_blob(blob_name)

        processor = StockProcessor()
        processor.process_xml_file(xml_string_from_blob, fallback_date=dt_obj)

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"[OK] Arquivo temporário removido: {temp_file_path}")

    print(f"[OK] Processamento finalizado")


if __name__ == "__main__":
    run()