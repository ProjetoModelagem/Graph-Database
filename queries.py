from neo4j import GraphDatabase
import random

# Configurações de conexão com o Neo4j
uri = "info" 
usuario = "info"
senha = "info"

# Inicializar o driver do Neo4j
driver = GraphDatabase.driver(uri, auth=(usuario, senha))

# Query que resolve o 1
def historico_aluno_aleatorio():
    with driver.session() as session:

        # Busca todos os alunos
        alunos_result = session.run("MATCH (a:Aluno) RETURN a.nome AS nome, a.id AS id")
        alunos = [record for record in alunos_result]

        if not alunos:
            print("Nenhum aluno encontrado.")
            return

        # Seleciona um aluno aleatoriamente
        aluno = random.choice(alunos)
        aluno_nome = aluno['nome']
        aluno_id = aluno['id']

        # Busca o historico escolar desse aluno
        result = session.run("MATCH (a:Aluno {id: $id})-[:CURSOU]->(d:Disciplina) "
                             "RETURN d.id AS codigo, d.nome AS disciplina, d.semestre AS semestre, d.ano AS ano, d.nota_final AS nota",
                             id=aluno_id)


        print(f"\nHistórico escolar de {aluno_nome}:")
        historico_set = set()
        for record in result:
            historico = (record['codigo'], record['disciplina'], record['semestre'], record['ano'], record['nota'])
            if historico not in historico_set:
                historico_set.add(historico)
                print(f"Código: {record['codigo']}, Disciplina: {record['disciplina']}, Semestre: {record['semestre']}, Ano: {record['ano']}, Nota Final: {record['nota']}")

        if not historico_set:
            print("Nenhum histórico escolar encontrado.")

# Query que resolve o 2
def historico_professor_aleatorio():
    with driver.session() as session:

        # Busca todos os professores
        professores_result = session.run("MATCH (p:Professor) RETURN p.nome AS nome, p.id AS id")
        professores = [record for record in professores_result]

        if not professores:
            print("Nenhum professor encontrado.")
            return


        # Seleciona um professor aleatoriamente
        professor = random.choice(professores)
        professor_nome = professor['nome']
        professor_id = professor['id']


        # Busca o historico de disciplinas ministradas por esse professor
        result = session.run("MATCH (p:Professor {id: $id})-[:MINISTROU]->(d:Disciplina) "
                             "RETURN d.nome AS disciplina, d.semestre AS semestre, d.ano AS ano",
                             id=professor_id)

        print(f"\nHistórico de disciplinas ministradas por {professor_nome}:")
        disciplinas_set = set()
        for record in result:
            disciplina_info = (record['disciplina'], record['semestre'], record['ano'])
            if disciplina_info not in disciplinas_set:
                disciplinas_set.add(disciplina_info)
                print(f"Disciplina: {record['disciplina']}, Semestre: {record['semestre']}, Ano: {record['ano']}")

        if not disciplinas_set:
            print("Nenhum histórico de disciplinas ministradas encontrado.")

# Query que resolve o 3
def alunos_formados(semestre, ano):
    with driver.session() as session:
        result = session.run("MATCH (a:Aluno)-[:CURSOU]->(d:Disciplina) "
                             "WHERE a.situacao_graduacao = true AND d.semestre = $semestre AND d.ano = $ano "
                             "RETURN DISTINCT a.nome AS aluno", semestre=semestre, ano=ano)
        alunos_set = set()
        print(f"\nAlunos formados no semestre {semestre} do ano {ano}:")
        for record in result:
            aluno_nome = record['aluno']
            if aluno_nome not in alunos_set:
                alunos_set.add(aluno_nome)
                print(f"- {aluno_nome}")

# Query que resolve o 4
def chefes_departamentos():
    with driver.session() as session:
        result = session.run("MATCH (p:Professor)-[:CHEFE_DE]->(d:Departamento) "
                             "RETURN p.nome AS professor, d.nome AS departamento")
        department_heads_set = set()
        print("\nProfessores que são chefes de departamento:")
        for record in result:
            department_head_info = (record['professor'], record['departamento'])
            if department_head_info not in department_heads_set:
                department_heads_set.add(department_head_info)
                print(f"Departamento: {record['departamento']}, Chefe: {record['professor']}")

# Query que resolve o 5
def info_grupo_tcc(grupo_numero):
    with driver.session() as session:
        result = session.run("MATCH (g:TCC {grupo_numero: $grupo_numero})-[:ORIENTA]-(p:Professor), "
                             "(g)<-[:MEMBRO_DO_GRUPO]-(a:Aluno) "
                             "RETURN g.grupo_numero AS grupo, p.nome AS orientador, a.nome AS aluno", grupo_numero=grupo_numero)
        orientador = None
        alunos_set = set()
        print(f"\nGrupo de TCC número {grupo_numero}:")

        for record in result:
            if not orientador:
                orientador = record['orientador']
            aluno_nome = record['aluno']
            if aluno_nome not in alunos_set:
                alunos_set.add(aluno_nome)

        if orientador:
            print(f"Orientador: {orientador}")
        else:
            print("Orientador não encontrado.")

        if alunos_set:
            print("Alunos:")
            for aluno in alunos_set:
                print(f"- {aluno}")
        else:
            print("Nenhum aluno encontrado.")


historico_aluno_aleatorio()
historico_professor_aleatorio()
alunos_formados(1, 2024)
chefes_departamentos()
info_grupo_tcc(2)

driver.close()
