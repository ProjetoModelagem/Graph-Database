# Projeto de Banco de Dados NoSQL com Neo4j

## Integrantes do Grupo
- **Guilherme de Abreu** - Matrícula: 22.222.028-7

## Projeto do semestre passado

- [Projeto](https://github.com/GuizinhoAB/Modelo-de-Banco-de-Dados/tree/main)

## Descrição do Projeto
Este projeto faz a migração de dados de um banco de dados relacional PostgreSQL para um banco de dados NoSQL, o **Neo4j**. O objetivo é armazenar as informações de alunos, professores, cursos, departamentos, disciplinas e grupos de TCC em um banco de grafos.

## Como Executar o Código

### 1. Instalar Dependências
- Para este projeto, use o Python 3.12, pois `psycopg2` pode apresentar problemas em outras versões mais recentes.
- Instale as bibliotecas necessárias executando o seguinte comando:
    ```bash
    pip install psycopg2 neo4j
    ```

### 2. Configurar o PostgreSQL e o Neo4j
- **PostgreSQL**: Certifique-se de que o banco de dados PostgreSQL está rodando. Recomenda-se o uso do pgAdmin para gerenciar e visualizar o banco de dados.
- **Neo4j**: Garanta que o Neo4j esteja corretamente conectado.
  - Acesse o **Neo4j Workspace** para visualizar e verificar a criação dos nós e relacionamentos.
  - Use as credenciais de acesso padrão ou as configuradas para o seu banco.

### 3. Executar os Scripts

- Primeiro, popule o banco de dados PostgreSQL:
    ```bash
    python criacao_tabela.py
    python data_generator.py
    ```

- Em seguida, execute os scripts de criação, migração e consultas:
    ```bash
    python criacao_colecao.py
    python migracao.py
    python queries.py
    ```

## Queries para a Criação das Estruturas Necessárias
As queries de criação de nós e relacionamentos estão em **criacao_colecao.py**.

## Código Desenvolvido para a Migração
- O código de migração para o Neo4j está em **migracao.py**.

## Queries que Resolvem os Itens Requeridos
- As queries de consulta estão em **queries.py**.

## Validação das Queries
Para garantir que os dados foram migrados corretamente, acesse o **Neo4j Workspace** (workspace-preview.neo4j.io/workspace/query), nele é exibido tudo.

## Descrição das Estruturas

### Estrutura dos Nós e Relacionamentos no Neo4j

1. alunos

```cypher
(:Aluno {data_nascimento: "2001-08-20", nome: "Olívia Silveira", id: 1, email: "vitoria82@example.org", situacao_graduacao: false, data_matricula: "2021-10-22"})
```

2. professores

```cypher
(:Professor {data_nascimento: "1992-07-08", nome: "Giovanna Moreira", id: 1, data_contratacao: "2018-07-28", email: "caleb26@example.net"})
```

3. cursos

```cypher
(:Curso {nome: "Pneumologista", id: 1})
```

4. disciplinas

```cypher
(:Disciplina {ano: 2024, nome: "Físico nuclear", id: 1, semestre: 5, nota_final: 2.78})

```

5. departamentos

```cypher
(:Departamento {nome: "Matemática e Estatística", id: 1, chefe: false})

```

6. grupos_tcc

```cypher
(:TCC {orientador_nome: "Hellena Cavalcanti", orientador_id: 41, grupo_numero: 8})

```