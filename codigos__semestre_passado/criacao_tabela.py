import os
import psycopg2


# Função para conectar ao banco de dados PostgreSQL
def connect_to_database():
    conn = psycopg2.connect(
        database="info",
        user="info",
        password="info",
        host="info",
        port="info"
    )
    return conn

# Função para criar tabelas
def create_tables(conn):

    # Criação da tabela de disciplinas
    create_disciplines_table = """
    CREATE TABLE IF NOT EXISTS disciplinas (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL
    );
    """

    # Criação da tabela de alunos
    create_students_table = """
    CREATE TABLE IF NOT EXISTS alunos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        data_nascimento DATE NOT NULL,
        data_matricula DATE NOT NULL,
        situacao_graduacao BOOLEAN NOT NULL
    );
    """

    # Criação da tabela de histórico escolar dos alunos
    create_student_history_table = """
    CREATE TABLE IF NOT EXISTS historico_escolar (
        id SERIAL PRIMARY KEY,
        aluno_id INTEGER REFERENCES alunos(id),
        disciplina_id INTEGER REFERENCES disciplinas(id),
        semestre INTEGER NOT NULL,
        ano INTEGER NOT NULL,
        nota_final FLOAT,
        UNIQUE (aluno_id, disciplina_id) -- Garante que cada aluno só tem uma entrada por disciplina
    );
    """

    # Criação da tabela de alunos formados
    create_student_graduated_table = """
    CREATE TABLE IF NOT EXISTS alunos_formados (
        id SERIAL PRIMARY KEY,
        aluno_id INTEGER REFERENCES alunos(id),
        semestre INTEGER NOT NULL,
        ano INTEGER NOT NULL
    );

    """
    
    # Criação da tabela de professores
    create_professors_table = """
    CREATE TABLE IF NOT EXISTS professores (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        data_nascimento DATE NOT NULL,
        data_contratacao DATE NOT NULL
    );
    """
    
    # Criação da tabela de histórico de disciplinas ministradas por professores
    create_discipline__professor_history_table = """
    CREATE TABLE IF NOT EXISTS historico_disciplina_professores (
        id SERIAL PRIMARY KEY,
        professor_id INTEGER REFERENCES professores(id),
        disciplina_id INTEGER REFERENCES disciplinas(id),
        semestre INTEGER NOT NULL,
        ano INTEGER NOT NULL
    );
    """
    
    # Criação da tabela de cursos
    create_courses_table = """
    CREATE TABLE IF NOT EXISTS cursos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL
    );
    """

    # Criação da tabela de departamentos
    create_departments = """
    CREATE TABLE IF NOT EXISTS departamentos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) UNIQUE NOT NULL
    );
    """

    # Criação da tabela de chefe de departamento
    create_departments_chiefs = """
    CREATE TABLE IF NOT EXISTS professores_departamentos (
        id SERIAL PRIMARY KEY,
        professor_id INTEGER REFERENCES professores(id),
        departamento_id INTEGER REFERENCES departamentos(id)
    );
    """

    # Criação da tabela de grupo de tcc
    create_tcc_group = """
    CREATE TABLE IF NOT EXISTS grupo_tcc (
        id SERIAL PRIMARY KEY,
        aluno_id INTEGER REFERENCES alunos(id),
        professor_orientador_id INTEGER REFERENCES professores(id),
        grupo INTEGER NOT NULL
    );
    """

    # Executar as queries para criar as tabelas
    with conn.cursor() as cur:
        cur.execute(create_disciplines_table)
        cur.execute(create_students_table)
        cur.execute(create_student_history_table)
        cur.execute(create_professors_table)
        cur.execute(create_discipline__professor_history_table)
        cur.execute(create_courses_table)
        cur.execute(create_departments)
        cur.execute(create_departments_chiefs)
        cur.execute(create_tcc_group)
        cur.execute(create_student_graduated_table)
        conn.commit()
        print("Tabelas criadas com sucesso")

# Criar as tabelas
conn = connect_to_database()
create_tables(conn)