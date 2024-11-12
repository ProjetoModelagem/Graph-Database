from datetime import datetime
import psycopg2
from neo4j import GraphDatabase

# Configurações de conexão com o PostgreSQL
pg_conn = psycopg2.connect(
    database="info",
    user="info",
    password="info",
    host="info",
    port="info"
)
pg_cursor = pg_conn.cursor()

# Configurações de conexão com o Neo4j
uri = "info" 
usuario = "info"
senha = "info"

# Inicializar o driver do Neo4j
driver = GraphDatabase.driver(uri, auth=(usuario, senha))

# Migrar alunos
def migrar_alunos():
    with driver.session() as session:
        pg_cursor.execute("SELECT * FROM alunos;")
        alunos = pg_cursor.fetchall()
        for aluno in alunos:
            aluno_id = aluno[0]
            nome = aluno[1]
            email = aluno[2]
            data_nascimento = aluno[3].isoformat()
            data_matricula = aluno[4].isoformat()
            situacao_graduacao = aluno[5]

            # cria o nó para o aluno
            session.run(
                "CREATE (a:Aluno {id: $id, nome: $nome, email: $email, data_nascimento: $data_nascimento, "
                "data_matricula: $data_matricula, situacao_graduacao: $situacao_graduacao})",
                id=aluno_id, nome=nome, email=email, data_nascimento=data_nascimento,
                data_matricula=data_matricula, situacao_graduacao=situacao_graduacao
            )


            # Obtem e cria nós para o historico escolar
            pg_cursor.execute("""
                SELECT he.disciplina_id, d.nome, he.semestre, he.ano, he.nota_final
                FROM historico_escolar he
                JOIN disciplinas d ON he.disciplina_id = d.id
                WHERE he.aluno_id = %s;
            """, (aluno_id,))
            historico = pg_cursor.fetchall()

            for registro in historico:
                session.run(
                    "MATCH (a:Aluno {id: $aluno_id}) "
                    "CREATE (d:Disciplina {id: $disciplina_id, nome: $nome_disciplina, semestre: $semestre, "
                    "ano: $ano, nota_final: $nota_final}) "
                    "CREATE (a)-[:CURSOU]->(d)",
                    aluno_id=aluno_id, disciplina_id=registro[0], nome_disciplina=registro[1],
                    semestre=registro[2], ano=registro[3], nota_final=registro[4]
                )

            # Obteem e criea relacionamento com o grupo de TCC
            pg_cursor.execute("""
                SELECT grupo, professor_orientador_id
                FROM grupo_tcc
                WHERE aluno_id = %s;
            """, (aluno_id,))
            tcc_info = pg_cursor.fetchone()
            if tcc_info:

                grupo_numero = tcc_info[0]
                orientador_id = tcc_info[1]
                pg_cursor.execute("SELECT nome FROM professores WHERE id = %s;", (orientador_id,))
                orientador_nome = pg_cursor.fetchone()[0]

                session.run(
                    "MATCH (a:Aluno {id: $aluno_id}) "
                    "CREATE (g:TCC {grupo_numero: $grupo_numero, orientador_id: $orientador_id, "
                    "orientador_nome: $orientador_nome}) "
                    "CREATE (a)-[:MEMBRO_DO_GRUPO]->(g)",
                    aluno_id=aluno_id, grupo_numero=grupo_numero,
                    orientador_id=orientador_id, orientador_nome=orientador_nome
                )



# Migrar professores
def migrar_professores():
    with driver.session() as session:
        pg_cursor.execute("SELECT * FROM professores;")
        professores = pg_cursor.fetchall()
        for professor in professores:
            professor_id = professor[0]
            nome = professor[1]
            email = professor[2]
            data_nascimento = professor[3].isoformat()
            data_contratacao = professor[4].isoformat()

            # Cria o nó para o professor
            session.run(
                "CREATE (p:Professor {id: $id, nome: $nome, email: $email, data_nascimento: $data_nascimento, "
                "data_contratacao: $data_contratacao})",
                id=professor_id, nome=nome, email=email,
                data_nascimento=data_nascimento, data_contratacao=data_contratacao
            )

            # Obtem e cria nós para as disciplinas ministradas
            pg_cursor.execute("""
                SELECT hdp.disciplina_id, d.nome, hdp.semestre, hdp.ano
                FROM historico_disciplina_professores hdp
                JOIN disciplinas d ON hdp.disciplina_id = d.id
                WHERE hdp.professor_id = %s;
            """, (professor_id,))

            disciplinas = pg_cursor.fetchall()
            for registro in disciplinas:
                session.run(
                    "MATCH (p:Professor {id: $professor_id}) "
                    "CREATE (d:Disciplina {id: $disciplina_id, nome: $nome_disciplina, semestre: $semestre, ano: $ano}) "
                    "CREATE (p)-[:MINISTROU]->(d)",
                    professor_id=professor_id, disciplina_id=registro[0],
                    nome_disciplina=registro[1], semestre=registro[2], ano=registro[3]
                )

            # Obtem e cria relacionamento com o departamento
            pg_cursor.execute("""
                SELECT d.id, d.nome, CASE WHEN pd.professor_id IS NOT NULL THEN true ELSE false END AS chefe
                FROM departamentos d
                LEFT JOIN professores_departamentos pd ON d.id = pd.departamento_id AND pd.professor_id = %s;
            """, (professor_id,))
            departamento = pg_cursor.fetchone()

            if departamento:
                session.run(
                    "MATCH (p:Professor {id: $professor_id}) "
                    "CREATE (d:Departamento {id: $departamento_id, nome: $nome, chefe: $chefe}) "
                    "CREATE (p)-[:PERTENCE_A]->(d)",
                    professor_id=professor_id, departamento_id=departamento[0],
                    nome=departamento[1], chefe=departamento[2]
                )

# Migrar cursos
def migrar_cursos():
    with driver.session() as session:
        pg_cursor.execute("SELECT * FROM cursos;")
        cursos = pg_cursor.fetchall()
        for curso in cursos:
            curso_id = curso[0]
            nome = curso[1]

            # Cria o nó para o curso
            session.run(
                "CREATE (c:Curso {id: $id, nome: $nome})",
                id=curso_id, nome=nome
            )

            # Cria os nós para a matriz curricular
            pg_cursor.execute("SELECT id, nome FROM disciplinas;")
            disciplinas = pg_cursor.fetchall()
            for disciplina in disciplinas:

                session.run(
                    "MATCH (c:Curso {id: $curso_id}) "
                    "CREATE (d:Disciplina {id: $disciplina_id, nome: $nome_disciplina}) "
                    "CREATE (c)-[:INCLUI]->(d)",
                    curso_id=curso_id, disciplina_id=disciplina[0], nome_disciplina=disciplina[1]
                )

# Migrar departamentos
def migrar_departamentos():
    with driver.session() as session:
        pg_cursor.execute("SELECT * FROM departamentos;")
        departamentos = pg_cursor.fetchall()
        for departamento in departamentos:
            departamento_id = departamento[0]
            nome = departamento[1]

            # Cria o nó pro departamento
            session.run(
                "CREATE (d:Departamento {id: $id, nome: $nome})",
                id=departamento_id, nome=nome
            )


            # Cria  relacionamento com o chefe do departamento
            pg_cursor.execute("""
                SELECT p.id, p.nome
                FROM professores_departamentos pd
                JOIN professores p ON pd.professor_id = p.id
                WHERE pd.departamento_id = %s;
            """, (departamento_id,))
            chefe = pg_cursor.fetchone()

            if chefe:
                session.run(
                    "MATCH (d:Departamento {id: $departamento_id}) "
                    "CREATE (p:Professor {id: $chefe_id, nome: $chefe_nome}) "
                    "CREATE (p)-[:CHEFE_DE]->(d)",
                    departamento_id=departamento_id, chefe_id=chefe[0], chefe_nome=chefe[1]
                )

# Migrar disciplinas
def migrar_disciplinas():
    with driver.session() as session:
        pg_cursor.execute("SELECT * FROM disciplinas;")
        disciplinas = pg_cursor.fetchall()
        for disciplina in disciplinas:
            session.run(
                "CREATE (d:Disciplina {id: $id, nome: $nome})",
                id=disciplina[0], nome=disciplina[1]
            )



# Migrar grupos de TCC
def migrar_grupos_tcc():
    with driver.session() as session:
        pg_cursor.execute("SELECT DISTINCT grupo FROM grupo_tcc;")
        grupos = pg_cursor.fetchall()
        for grupo in grupos:
            grupo_numero = grupo[0]

            # Cria o nó pro grupo de TCC
            session.run(
                "CREATE (g:TCC {grupo_numero: $grupo_numero})",
                grupo_numero=grupo_numero
            )

            # Cria relacionamento com o orientador
            pg_cursor.execute("""
                SELECT DISTINCT p.id, p.nome
                FROM grupo_tcc gt
                JOIN professores p ON gt.professor_orientador_id = p.id
                WHERE gt.grupo = %s;
            """, (grupo_numero,))

            orientador = pg_cursor.fetchone()
            if orientador:

                session.run(
                    "MATCH (g:TCC {grupo_numero: $grupo_numero}) "
                    "CREATE (p:Professor {id: $orientador_id, nome: $orientador_nome}) "
                    "CREATE (p)-[:ORIENTA]->(g)",
                    grupo_numero=grupo_numero, orientador_id=orientador[0], orientador_nome=orientador[1]
                )


            # Cria relacionamentos com os alunos do grupo
            pg_cursor.execute("""
                SELECT a.id, a.nome
                FROM grupo_tcc gt
                JOIN alunos a ON gt.aluno_id = a.id
                WHERE gt.grupo = %s;
            """, (grupo_numero,))
            alunos = pg_cursor.fetchall()
            for aluno in alunos:
                session.run(
                    "MATCH (g:TCC {grupo_numero: $grupo_numero}) "
                    "CREATE (a:Aluno {id: $aluno_id, nome: $aluno_nome}) "
                    "CREATE (a)-[:MEMBRO_DO_GRUPO]->(g)",
                    grupo_numero=grupo_numero, aluno_id=aluno[0], aluno_nome=aluno[1]
                )

migrar_alunos()
print("Alunos inseridos")
migrar_professores()
print("Professores inseridos")
migrar_cursos()
print("Cursos inseridos")
migrar_departamentos()
print("Departamentos inseridos")
migrar_disciplinas()
print("Disciplinas inseridas")
migrar_grupos_tcc()
print("Grupo tcc inseridos")

print("Migração concluída com sucesso!")

driver.close()
