import os
import sqlite3
import psycopg
from datetime import datetime

# Configurações de conexão (Prioriza variáveis de ambiente)
PG_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "dbname": os.environ.get("DB_NAME", "db_safira_musicloud"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "xbala"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "client_encoding": "UTF8"
}

# Caminho do banco SQLite3 atual
SQLITE_DB = 'instance/safira.db'

# Mapeamento de Tabelas e Colunas: SQLite (Inglês) -> PostgreSQL (Português)
SCHEMA_MAPPING = {
    'users': {
        'table': 'usuarios',
        'columns': {
            'id': 'id',
            'username': 'usuario',
            'password_hash': 'senha_hash'
        }
    },
    'people': {
        'table': 'pessoas',
        'columns': {
            'id': 'id',
            'name': 'nome',
            'type': 'tipo',
            'email': 'email',
            'phone': 'telefone',
            'birth_date': 'data_nascimento',
            'has_guardian': 'possui_responsavel',
            'guardian_name': 'nome_responsavel',
            'guardian_phone': 'telefone_responsavel',
            'cpf': 'cpf',
            'guardian_cpf': 'cpf_responsavel',
            'active': 'ativo'
        }
    },
    'courses': {
        'table': 'cursos',
        'columns': {
            'id': 'id',
            'name': 'nome',
            'workload': 'carga_horaria',
            'teacher_id': 'professor_id'
        }
    },
    'schedules': {
        'table': 'agendas',
        'columns': {
            'id': 'id',
            'teacher_id': 'professor_id',
            'day_of_week': 'dia_semana',
            'start_time': 'hora_inicio',
            'end_time': 'hora_fim',
            'course_name': 'nome_curso',
            'room': 'sala'
        }
    },
    'attendance': {
        'table': 'presencas',
        'columns': {
            'id': 'id',
            'schedule_id': 'agenda_id',
            'student_id': 'aluno_id',
            'date': 'data',
            'status': 'status'
        }
    },
    'finance': {
        'table': 'financeiro',
        'columns': {
            'id': 'id',
            'description': 'descricao',
            'amount': 'valor',
            'type': 'tipo',
            'date': 'data',
            'status': 'status'
        }
    }
}

def create_tables(pg_conn):
    """Cria a estrutura de tabelas no PostgreSQL com nomes e colunas em Português."""
    with pg_conn.cursor() as cur:
        print("[ Safira MusicLoud ] >> Criando tabelas traduzidas no PostgreSQL...")

        cur.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                usuario TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS pessoas (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                email TEXT,
                telefone TEXT,
                data_nascimento TEXT,
                possui_responsavel INTEGER DEFAULT 0,
                nome_responsavel TEXT,
                telefone_responsavel TEXT,
                cpf TEXT,
                cpf_responsavel TEXT,
                ativo INTEGER DEFAULT 1
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS cursos (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                carga_horaria INTEGER,
                professor_id INTEGER REFERENCES pessoas(id) ON DELETE SET NULL
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS agendas (
                id SERIAL PRIMARY KEY,
                professor_id INTEGER REFERENCES pessoas(id) ON DELETE CASCADE,
                dia_semana TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fim TEXT NOT NULL,
                nome_curso TEXT,
                sala TEXT
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS presencas (
                id SERIAL PRIMARY KEY,
                agenda_id INTEGER REFERENCES agendas(id) ON DELETE CASCADE,
                aluno_id INTEGER REFERENCES pessoas(id) ON DELETE CASCADE,
                data TEXT NOT NULL,
                status TEXT NOT NULL
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS financeiro (
                id SERIAL PRIMARY KEY,
                descricao TEXT NOT NULL,
                valor DOUBLE PRECISION NOT NULL,
                tipo TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT NOT NULL
            );
        ''')
        pg_conn.commit()
    print("[ Safira MusicLoud ] >> Tabelas criadas/verificadas com sucesso.")

def update_sequences(pg_conn):
    """Sincroniza as sequências dos IDs após a migração dos dados."""
    tables_pg = [m['table'] for m in SCHEMA_MAPPING.values()]
    with pg_conn.cursor() as cur:
        for table in tables_pg:
            cur.execute(f"""
                SELECT setval(pg_get_serial_sequence('{table}', 'id'),
                COALESCE(MAX(id), 1),
                MAX(id) IS NOT NULL) FROM {table};
            """)
        pg_conn.commit()
    print("[ Safira MusicLoud ] >> Sequências de ID atualizadas.")

def migrate_data():
    """Migra dados do SQLite (Inglês) para PostgreSQL (Português)."""
    if not os.path.exists(SQLITE_DB):
        print(f"[ Safira MusicLoud ] >> Erro: Arquivo {SQLITE_DB} não encontrado.")
        return

    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    try:
        with psycopg.connect(**PG_CONFIG) as pg_conn:
            print("\n[ Safira MusicLoud ] >> Iniciando migração traduzida...\n")
            create_tables(pg_conn)

            # Ordem de migração
            migration_order = ['users', 'people', 'courses', 'schedules', 'attendance', 'finance']

            for table_sqlite in migration_order:
                mapping = SCHEMA_MAPPING[table_sqlite]
                table_pg = mapping['table']
                col_map = mapping['columns']

                sqlite_cur.execute(f"SELECT * FROM {table_sqlite}")
                rows = sqlite_cur.fetchall()

                if not rows:
                    print(f"[ Safira MusicLoud ] >> Tabela '{table_sqlite}' sem dados.")
                    continue

                pg_cols = [col_map[c] for c in rows[0].keys()]
                col_names = ", ".join(pg_cols)
                placeholders = ", ".join(["%s"] * len(pg_cols))

                query = f"INSERT INTO {table_pg} ({col_names}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING"

                valid_data = []
                with pg_conn.cursor() as pg_cur:
                    for row in rows:
                        row_dict = dict(row)

                        # Tradução de valores específicos
                        if table_sqlite == 'people':
                            if row_dict['type'] == 'teacher': row_dict['type'] = 'professor'
                            elif row_dict['type'] == 'student': row_dict['type'] = 'aluno'

                        # Validação de integridade referencial
                        is_valid = True
                        if table_sqlite == 'courses' and row_dict['teacher_id']:
                            pg_cur.execute("SELECT 1 FROM pessoas WHERE id = %s", (row_dict['teacher_id'],))
                            if not pg_cur.fetchone(): is_valid = False
                        elif table_sqlite == 'schedules' and row_dict['teacher_id']:
                            pg_cur.execute("SELECT 1 FROM pessoas WHERE id = %s", (row_dict['teacher_id'],))
                            if not pg_cur.fetchone(): is_valid = False
                        elif table_sqlite == 'attendance':
                            pg_cur.execute("SELECT 1 FROM agendas WHERE id = %s", (row_dict['schedule_id'],))
                            if not pg_cur.fetchone(): is_valid = False
                            pg_cur.execute("SELECT 1 FROM pessoas WHERE id = %s", (row_dict['student_id'],))
                            if not pg_cur.fetchone(): is_valid = False

                        if is_valid:
                            # Monta os valores na ordem das colunas traduzidas
                            data_tuple = tuple(row_dict[c] for c in rows[0].keys())
                            valid_data.append(data_tuple)
                        else:
                            print(f"  [AVISO] Pulando registro ID {row_dict.get('id')} da tabela {table_sqlite} por erro de vínculo.")

                    if valid_data:
                        pg_cur.executemany(query, valid_data)

                print(f"[ Safira MusicLoud ] >> {len(valid_data)} registros migrados para '{table_pg}'.")

            update_sequences(pg_conn)
            pg_conn.commit()
            print("\n[ Safira MusicLoud ] >> MIGRAÇÃO CONCLUÍDA COM SUCESSO! 🚀\n")

    except Exception as erro:
        print(f"\n[ Safira MusicLoud ] >> ERRO NA MIGRAÇÃO: {erro}\n")
    finally:
        sqlite_conn.close()

if __name__ == "__main__":
    migrate_data()
