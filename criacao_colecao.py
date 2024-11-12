from neo4j import GraphDatabase

# Configurações de conexão com o Neo4j
uri = "info" 
usuario = "info"
senha = "info"

# Inicializar o driver do Neo4j
driver = GraphDatabase.driver(uri, auth=(usuario, senha))

# Criar
def criar_colecoes():

    with driver.session() as session:

        # Cria os nós representando as colecoes no Neo4j
        session.run("MERGE (:Colecao {nome: 'alunos'})")
        session.run("MERGE (:Colecao {nome: 'cursos'})")
        session.run("MERGE (:Colecao {nome: 'departamentos'})")
        session.run("MERGE (:Colecao {nome: 'disciplinas'})")
        session.run("MERGE (:Colecao {nome: 'grupos_tcc'})")
        session.run("MERGE (:Colecao {nome: 'professores'})")

    print("Nós representando coleções criados com sucesso!")


criar_colecoes()


driver.close()
