import os
import psycopg
from psycopg.rows import dict_row
from werkzeug.security import generate_password_hash

# Configurações de conexão (Prioriza variáveis de ambiente)
PG_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "dbname": os.environ.get("DB_NAME", "db_safira_musicloud"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "xbala"),
    "port": int(os.environ.get("DB_PORT", 5432)),
}

def get_db():
    """Retorna uma conexão com o banco de dados PostgreSQL."""
    conn = psycopg.connect(**PG_CONFIG, row_factory=dict_row)
    return conn

def init_db():
    """Inicializa o esquema do banco de dados no PostgreSQL com nomes traduzidos."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Tabela de Usuários
                cur.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    usuario TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL
                )
                ''')

                # Criar usuário administrador se não existir
                cur.execute("SELECT * FROM usuarios WHERE usuario = %s", ('adm',))
                if not cur.fetchone():
                    senha_hash = generate_password_hash('adm')
                    cur.execute("INSERT INTO usuarios (usuario, senha_hash) VALUES (%s, %s)", ('adm', senha_hash))

                # Tabela de Pessoas
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
                )
                ''')

                # Tabela de Cursos
                cur.execute('''
                CREATE TABLE IF NOT EXISTS cursos (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    carga_horaria INTEGER,
                    professor_id INTEGER REFERENCES pessoas (id) ON DELETE SET NULL
                )
                ''')

                # Tabela de Agenda
                cur.execute('''
                CREATE TABLE IF NOT EXISTS agendas (
                    id SERIAL PRIMARY KEY,
                    professor_id INTEGER REFERENCES pessoas (id) ON DELETE CASCADE,
                    dia_semana TEXT NOT NULL,
                    hora_inicio TEXT NOT NULL,
                    hora_fim TEXT NOT NULL,
                    nome_curso TEXT,
                    sala TEXT
                )
                ''')

                # Tabela de Presença
                cur.execute('''
                CREATE TABLE IF NOT EXISTS presencas (
                    id SERIAL PRIMARY KEY,
                    agenda_id INTEGER REFERENCES agendas (id) ON DELETE CASCADE,
                    aluno_id INTEGER REFERENCES pessoas (id) ON DELETE CASCADE,
                    data TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                ''')

                # Tabela Financeira
                cur.execute('''
                CREATE TABLE IF NOT EXISTS financeiro (
                    id SERIAL PRIMARY KEY,
                    descricao TEXT NOT NULL,
                    valor DOUBLE PRECISION NOT NULL,
                    tipo TEXT NOT NULL,
                    data TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                ''')
                conn.commit()
    except Exception as e:
        print(f"Erro ao inicializar banco PostgreSQL: {e}")
