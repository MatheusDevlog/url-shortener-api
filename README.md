# URL Shortener API

API de encurtamento de URLs com Django e PostgreSQL. Implementa criação, listagem e consulta de links, redirecionamento e contador de acessos.

## Tecnologias

Python, Django, Django REST Framework, PostgreSQL e Docker Compose.

## Estrutura

- `config/`: configurações e rotas gerais do Django.
- `links/`: modelo, serializer, view, rotas e testes dos links.
- `manage.py`: comandos de gerenciamento do Django.
- `compose.yaml`: banco PostgreSQL para desenvolvimento local.

## Preparar o ambiente local

Requer Python 3.14 e Docker com Compose. Na primeira execução, crie `.env` a partir de `.env.example` e substitua `DJANGO_SECRET_KEY` e `POSTGRES_PASSWORD` por valores aleatórios. Mantenha os demais valores do exemplo para usar o PostgreSQL na porta 5432.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` antes de iniciar o banco. O arquivo é ignorado pelo Git. Se já existir, não o substitua com `cp`.

Depois de configurar os valores:

```bash
docker compose config --quiet
docker compose up -d db
docker compose exec db sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
set -a
source .env
set +a
.venv/bin/python manage.py migrate
.venv/bin/python manage.py showmigrations links
```

O comando `pg_isready` deve indicar que o banco aceita conexões; `showmigrations links` deve mostrar `[X] 0001_initial`.

## Executar a API

Na raiz do projeto, com o banco iniciado, carregue as variáveis e inicie o servidor local:

```bash
set -a
source .env
set +a
.venv/bin/python manage.py runserver
```

## Criar um link

`POST /api/links/` recebe `original_url`. A URL deve usar HTTP ou HTTPS e ter no máximo 2.048 caracteres. O endpoint é público e não exige autenticação.

Com o servidor iniciado, execute em outro terminal:

```bash
curl -i -X POST http://127.0.0.1:8000/api/links/ \
  -H 'Content-Type: application/json' \
  -d '{"original_url":"https://www.djangoproject.com/"}'
```

A resposta de sucesso tem status `201 Created` e os campos `id`, `original_url`, `code`, `short_url`, `access_count` e `created_at`. O código tem oito caracteres e o contador começa em zero. Uma entrada inválida retorna `400 Bad Request`.

O servidor controla o código, o contador e a data de criação. Cada criação produz um novo link, mesmo quando a URL original já foi cadastrada. O banco garante a unicidade do código; em caso de colisão, a API tenta gerar outro, com limite de cinco tentativas. Se todas colidirem, retorna `500`.

O campo `short_url` usa o endereço da requisição e pode ser acessado para redirecionar à URL original.

## Listar e consultar links

Os endpoints são públicos, não exigem autenticação e não recebem corpo:

| Método e caminho | Resultado |
| --- | --- |
| GET /api/links/ | 200 com uma lista de links, dos mais recentes aos mais antigos |
| GET /api/links/<code>/ | 200 com os dados do link identificado pelo código |

A listagem retorna todos os registros, sem paginação. Se não houver links, retorna uma lista vazia (`[]`). Cada registro contém `id`, `original_url`, `code`, `short_url`, `access_count` e `created_at`. A consulta de um código inexistente retorna `404`.

Listar ou consultar os dados não incrementa o contador. Somente acessar a URL de redirecionamento registra um acesso. A consulta individual permite apenas leitura; POST, PUT, PATCH e DELETE retornam `405`.

Para verificar no Thunder Client:

1. Envie GET para `http://127.0.0.1:8000/api/links/`.
2. Copie um código da resposta e envie GET para `http://127.0.0.1:8000/api/links/<code>/`, substituindo `<code>` pelo valor copiado.
3. Anote o contador, acesse a `short_url` uma vez e consulte os dados novamente. O contador deve aumentar em um; repetir apenas a consulta deve manter esse valor.
4. Consulte um código inexistente e confirme o status 404.

## Redirecionar um link

`GET /<code>/` recebe o código criado pela API, incrementa o contador e responde com `302 Found`. O cabeçalho `Location` contém a URL original; navegadores normalmente seguem esse destino automaticamente. O endpoint é público, não exige autenticação e não recebe corpo.

Cada GET válido soma um acesso, inclusive acessos repetidos. O contador registra requisições, não pessoas únicas. O incremento usa uma expressão `F()` no banco para evitar perda de contagem em acessos simultâneos. A resposta inclui instruções contra armazenamento em cache.

Um código inexistente retorna `404`. Métodos diferentes de GET, incluindo POST e HEAD, retornam `405`, sem incrementar o contador.

### Verificação manual com Thunder Client

Com o servidor local iniciado:

1. Envie o POST de criação e copie a `short_url` retornada.
2. Desative o seguimento automático de redirecionamentos (Follow Redirects) nas configurações do Thunder Client para observar a resposta da API.
3. Envie um GET para a `short_url`, sem corpo ou autenticação.

Resultados esperados:

| Requisição | Resultado |
| --- | --- |
| GET na URL curta existente | 302 e cabeçalho Location com a URL original |
| GET com código inexistente | 404 |
| POST na URL curta | 405 |

Os testes automatizados também verificam a contagem salva no banco. Para experimentar o comportamento no navegador, abra a URL curta; ele deve encaminhar para a página original.

## Testes

Instale as dependências de desenvolvimento e execute os testes com o PostgreSQL iniciado:

```bash
.venv/bin/pip install -r requirements-dev.txt
set -a
source .env
set +a
.venv/bin/python -m pytest -q
```

Os testes de integração verificam criação, validação, campos controlados pelo servidor, colisões de código, listagem, consulta por código, redirecionamento, contagem de acessos e métodos HTTP permitidos. O teste de métodos do redirecionamento mantém a verificação CSRF ativa para reproduzir requisições reais sem token. O pytest-django cria um banco de testes separado; o usuário PostgreSQL precisa ter permissão para criar bancos, como ocorre na configuração local do Compose.
