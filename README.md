# Projeto: Aprimoramento da Workout API

## Descrição:

Este projeto consiste em aprimorar a Workout API, implementando novas funcionalidades e melhorias para torná-la mais robusta e útil. A API original, disponível no repositório https://github.com/digitalinnovationone/workout_api, serviu como base para as modificações realizadas.

## Funcionalidades Implementadas:

1. **Adição de Query Parameters nos Endpoints:**
   - Foram adicionados parâmetros de consulta nos endpoints relacionados aos atletas, permitindo a busca por nome e CPF.

2. **Customização da Response de Retorno:**
   - No endpoint de obtenção de todos os atletas, a resposta agora inclui informações adicionais, como nome do atleta, centro de treinamento e categoria.

3. **Manipulação de Exceções de Integridade de Dados:**
   - Foi implementada a manipulação de exceções de integridade de dados em cada módulo/tabela da API. Quando ocorre uma exceção do tipo `sqlalchemy.exc.IntegrityError`, a API agora retorna uma mensagem indicando que já existe um atleta cadastrado com o CPF especificado, acompanhada de um status code 303.

4. **Adição de Paginação:**
   - A paginação foi adicionada utilizando a biblioteca `fastapi-pagination`, permitindo a especificação de limites e deslocamentos para a obtenção de resultados em partes.

## Como Utilizar:

Para utilizar a API aprimorada, siga as instruções abaixo:

1. Clone o repositório para sua máquina local.
2. Instale as dependências necessárias utilizando o gerenciador de pacotes de sua escolha (por exemplo, `pip` para Python).
3. Execute a aplicação utilizando o comando apropriado para o seu ambiente de desenvolvimento.
4. Acesse os endpoints da API conforme documentado na própria aplicação ou na documentação fornecida.

## Contribuição:

Contribuições são bem-vindas! Sinta-se à vontade para abrir um pull request com sugestões de melhorias, correções de bugs ou novas funcionalidades.

## Agradecimentos:

Agradeço à Digital Innovation One pela oportunidade de aprendizado e à comunidade de desenvolvedores por compartilhar conhecimento e experiências.
