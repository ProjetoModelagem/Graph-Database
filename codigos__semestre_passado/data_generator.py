
import os
import psycopg2
from faker import Faker
import random

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

# Conectar ao banco de dados
conn = connect_to_database()

# Função para gerar alunos
def insert_students(conn, num_students):
    fake = Faker('pt_BR')
    students_with_40_courses = 0  # Contador de alunos com 40 disciplinas cursadas
    max_disciplinas_cursadas = 40  # Número máximo de disciplinas cursadas
    print("Inserindo em alunos...")
    with conn.cursor() as cur:
        # Consulta para obter todos os IDs de disciplinas
        cur.execute("SELECT id FROM disciplinas;")
        disciplina_ids = [row[0] for row in cur.fetchall()]

        # Inserção de dados de alunos com histórico escolar
        for _ in range(num_students):
            nome = fake.name()
            email = fake.email()
            data_nascimento = fake.date_of_birth(minimum_age=18, maximum_age=30)
            data_matricula = fake.date_between(start_date='-4y', end_date='today')
            situacao_graduacao = fake.boolean(chance_of_getting_true=80)  # Assume 80% de chance de graduação
            
            # Inserção de dados do aluno
            cur.execute("""
                INSERT INTO alunos (nome, email, data_nascimento, data_matricula, situacao_graduacao)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (nome, email, data_nascimento, data_matricula, situacao_graduacao))
            aluno_id = cur.fetchone()[0]
            
            # Verifica se o número máximo de alunos com 40 disciplinas já foi alcançado
            if students_with_40_courses < 10:
                # Gera o histórico escolar para o aluno com 40 disciplinas
                generate_course_history(cur, aluno_id, disciplina_ids, max_disciplinas_cursadas)
                students_with_40_courses += 1
            else:
                # Gera o histórico escolar para o aluno com um número randomizado de disciplinas entre 1 e 39
                num_disciplinas_cursadas = random.randint(1, max_disciplinas_cursadas - 1)
                generate_course_history(cur, aluno_id, disciplina_ids, num_disciplinas_cursadas)

    print("Inserido em alunos.")
    conn.commit()


# Função para gerar o histórico escolar para cada aluno
def generate_course_history(cur, aluno_id, disciplina_ids, num_disciplinas_cursadas):
    print("Inserindo na tabela de histórico escolar...")
    disciplinas_escolhidas = random.sample(disciplina_ids, num_disciplinas_cursadas)
    for disciplina_id in disciplinas_escolhidas:
        semestre = random.randint(1, 8)  # Exemplo: semestre 1 ou 8
        ano = random.randint(2015, 2024)  # Exemplo: ano entre 2015 e 2024
        nota_final = round(random.uniform(0, 10), 2)  # Exemplo: nota final entre 0 e 10
        cur.execute("""
            INSERT INTO historico_escolar (aluno_id, disciplina_id, semestre, ano, nota_final)
            VALUES (%s, %s, %s, %s, %s);
        """, (aluno_id, disciplina_id, semestre, ano, nota_final))
    print("Inserido na tabela de histórico escolar.")
    

# Função para gerar alunos formados
def generate_graduated_students(conn):
    print("inserindo na tabela de alunos formados")
    with conn.cursor() as cur:
        # Selecionar alunos que possuem exatamente 40 disciplinas cursadas (Toda matriz curricular de um Curso)
        cur.execute("""
            SELECT aluno_id
            FROM (
                SELECT aluno_id, COUNT(*) AS num_disciplinas
                FROM historico_escolar
                GROUP BY aluno_id
            ) AS disciplinas_por_aluno
            WHERE num_disciplinas = 40;
        """)
        alunos_aptos = [row[0] for row in cur.fetchall()]
        
        # Inserir alunos aptos na tabela de alunos formados
        for aluno_id in alunos_aptos:
            # Gerar semestre e ano aleatórios
            semestre = random.randint(1, 2)
            ano = random.randint(2015, 2024)
            
            cur.execute("""
                INSERT INTO alunos_formados (aluno_id, semestre, ano)
                VALUES (%s, %s, %s);
            """, (aluno_id, semestre, ano))
        
        print("inserido na tabela de alunos formados")
        conn.commit()


# Função para gerar professores
def insert_professors(conn, num_professors):
    fake = Faker('pt_BR')
    print("Inserindo na tabela de professor")
    with conn.cursor() as cur:
        # Consulta para obter todos os IDs de disciplinas uma vez
        cur.execute("SELECT id FROM disciplinas;")
        disciplina_ids = [row[0] for row in cur.fetchall()]

        # Gerar dados e inserir os professores
        for _ in range(num_professors):
            nome = fake.name()
            email = fake.email()
            data_nascimento = fake.date_of_birth(minimum_age=30, maximum_age=60)
            data_contratacao = fake.date_between(start_date='-10y', end_date='today')
            cur.execute("""
                INSERT INTO professores (nome, email, data_nascimento, data_contratacao)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (nome, email, data_nascimento, data_contratacao))
            professor_id = cur.fetchone()[0]
            
            # Gerar histórico de disciplinas ministradas pelo professor
            max_disciplinas_ministradas = 5
            generate_course_history_for_professor(cur, professor_id, disciplina_ids, max_disciplinas_ministradas)
        
        print("Inserido na tabela de professor")
        conn.commit()


# Função para gerar histórico de disciplinas ministradas para cada professor
def generate_course_history_for_professor(cur, professor_id, disciplina_ids, max_disciplinas_ministradas):
    num_disciplinas_ministradas = random.randint(1, max_disciplinas_ministradas)
    disciplinas_ministradas = random.sample(disciplina_ids, num_disciplinas_ministradas)
    print("Inserindo em disciplina ministrada por professor")
    for disciplina_id in disciplinas_ministradas:
        semestre = random.randint(1, 8)  # Exemplo: semestre 1 ou 8
        ano = random.randint(2015, 2024)  # Exemplo: ano entre 2015 e 2024
        cur.execute("""
            INSERT INTO historico_disciplina_professores (professor_id, disciplina_id, semestre, ano)
            VALUES (%s, %s, %s, %s);
        """, (professor_id, disciplina_id, semestre, ano))
    print("Inserido na tabela de disciplinas ministrada por professor")


# Função para gerar departamentos
def insert_departments(conn, departamentos):
    print("Inserindo em departamento")
    # Lista de nomes de departamentos a serem inseridos
    departamentos = [
        "Matemática e Estatística",
        "Física",
        "Ciências Biológicas",
        "Química",
        "Ciências Humanas",
        "Ciências Sociais",
        "Ciências da Computação",
        "Economia",
        "Administração",
        "Artes e Humanidades"
    ]
    with conn.cursor() as cur:
        for departamento in departamentos:
            # Inserção do departamento no banco de dados
            cur.execute("INSERT INTO departamentos (nome) VALUES (%s) RETURNING id;", (departamento,))
            departamento_id = cur.fetchone()[0]
            # Commit após cada inserção para garantir que os dados sejam salvos
            conn.commit()
    print("Dados inseridos na tabela de departamentos.")


# Função para gerar chefes de departamentos
def assign_department_chiefs(conn):
    print("Inserindo em chefe de departamento")
    cur = conn.cursor()
    # Selecionar todos os IDs de professores
    cur.execute("SELECT id FROM professores;")
    professor_ids = [row[0] for row in cur.fetchall()]

    # Selecionar todos os IDs de departamentos
    cur.execute("SELECT id FROM departamentos;")
    department_ids = [row[0] for row in cur.fetchall()]

    with conn.cursor() as cur:
        for department_id in department_ids:
            # Escolher aleatoriamente um professor para ser o chefe do departamento
            chief_id = random.choice(professor_ids)
            # Inserir a relação entre o professor e o departamento
            cur.execute("INSERT INTO professores_departamentos (professor_id, departamento_id) VALUES (%s, %s);", (chief_id, department_id))
            # Commit após cada inserção para garantir que os dados sejam salvos
            conn.commit()
    print("Dados inseridos na tabela de chefe de departamento.")


# Função para gerar cursos
def insert_courses(conn, num_courses):
    print("Inserindo em cursos")
    fake = Faker('pt_BR')
    with conn.cursor() as cur:
        for _ in range(num_courses):
            # Gerar um nome de curso
            nome_curso = fake.job()
            cur.execute("""
                INSERT INTO cursos (nome)
                VALUES (%s);
            """, (nome_curso,))            
        conn.commit()
    print("Dados inseridos na tabela de cursos.")    


# Função para gerar disciplinas
def insert_disciplines(conn, num_disciplinas):
    fake = Faker('pt_BR')
    print("Inserindo em disciplinas")
    with conn.cursor() as cur:
        for _ in range(num_disciplinas):
            # Gerar um nome de disciplina aleatório
            nome_disciplina = fake.job()
            cur.execute("""
                INSERT INTO disciplinas (nome)
                VALUES (%s);
            """, (nome_disciplina,))
        print("Dados inseridos na tabela disciplinas.")
        conn.commit()


# Função para gerar grupos de tcc
def insert_tcc_groups(conn, num_groups, num_students_per_group):
    print("Inserindo em grupo de TCC")
    cur = conn.cursor()
    try:
        # Consulta para obter todos os IDs de professores e alunos uma vez
        cur.execute("SELECT id FROM professores;")
        professor_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT id FROM alunos;")
        aluno_ids = [row[0] for row in cur.fetchall()]

        for group in range(1, num_groups + 1):
            # Escolhendo aleatoriamente um professor para ser o orientador do grupo
            professor_id = random.choice(professor_ids)
            
            # Inserindo um grupo de alunos com o mesmo orientador
            grupo_data = []
            for _ in range(num_students_per_group):
                # Escolhendo aleatoriamente um aluno
                aluno_id = random.choice(aluno_ids)
                grupo_data.append((aluno_id, professor_id, group))
                
            # Inserindo os alunos no grupo TCC com o professor orientador e número do grupo
            cur.executemany("""
                INSERT INTO grupo_tcc (aluno_id, professor_orientador_id, grupo)
                VALUES (%s, %s, %s);
            """, grupo_data)
            
        conn.commit()
        print("Dados inseridos na tabela de grupo TCC.")
    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao inserir dados na tabela de grupo TCC:", e)
    finally:
        cur.close()
    print("Dados inseridos na tabela de TCC.")



# Quantidade de disciplinas a serem inseridas
num_disciplines_to_insert = 100
insert_disciplines(conn, num_disciplines_to_insert)  # Inserir disciplinas

# Quantidade de cursos a serem inseridos
num_courses_to_insert = 10
insert_courses(conn, num_courses_to_insert)  # Inserir cursos

# Quantidade de alunos a serem inseridos
num_students_to_insert = 100
insert_students(conn, num_students_to_insert)  # Inserir alunos

# Quantidade de professores a serem inseridos
num_professors_to_insert = 50
insert_professors(conn, num_professors_to_insert)  # Inserir professores

generate_graduated_students(conn)  # Gerar alunos formados

# Quantidade de departamentos a serem inseridos
num_departments_to_insert = 10
insert_departments(conn, num_departments_to_insert)  # Inserir departamentos

assign_department_chiefs(conn)  # Atribuir chefes de departamento

# Inserir grupos de TCC
num_groups = 10 
num_students_per_group = 5
insert_tcc_groups(conn, num_groups, num_students_per_group)  # Inserir grupos de TCC

print("Dados inseridos com sucesso")

# Fechar a conexão
conn.close()
