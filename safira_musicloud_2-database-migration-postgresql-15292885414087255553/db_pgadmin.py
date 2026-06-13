import os
import psycopg
from datetime import datetime

# Força UTF-8 no ambiente (resolve erro de decode no Windows)
os.environ["PGCLIENTENCODING"] = "UTF8"
os.environ["PYTHONUTF8"] = "1"

def testar_conexao():
    print("\n[ Safira MusicLoud ] >> Iniciando comunicação com o banco...\n")

    try:
        with psycopg.connect(
            host="localhost",
            dbname="db_safira_musicloud",
            user="postgres",
            password="xbala",
            port=5432,
            client_encoding="UTF8"
        ) as conn:

            print("==============================================")
            print("[ Safira MusicLoud ] >> DATABASE STATUS: ONLINE ✅")
            print("Conectado em:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            print("==============================================")

    except Exception as erro:
        print("==============================================")
        print("[ Safira MusicLoud ] >> DATABASE STATUS: OFFLINE ❌")
        print("Erro técnico:", erro)
        print("==============================================")


if __name__ == "__main__":
    testar_conexao()
