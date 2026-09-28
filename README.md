# URL Shortener API

API de encurtamento de URLs com Django e PostgreSQL. A criação de links está implementada; o redirecionamento e os demais endpoints ainda estão em desenvolvimento.

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

O campo `short_url` usa o endereço da requisição. O redirecionamento por essa URL ainda não está implementado.

## Testes

Instale as dependências de desenvolvimento e execute os testes com o PostgreSQL iniciado:

```bash
.venv/bin/pip install -r requirements-dev.txt
set -a
source .env
set +a
.venv/bin/python -m pytest -q
```

Os testes de integração verificam criação, validação, campos controlados pelo servidor, colisões de código e métodos HTTP permitidos. O pytest-django cria um banco de testes separado; o usuário PostgreSQL precisa ter permissão para criar bancos, como ocorre na configuração local do Compose.
