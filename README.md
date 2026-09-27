# URL Shortener API

API para criar links curtos e redirecionar para as URLs originais. O projeto está na etapa de estrutura inicial; os endpoints ainda não foram implementados.

## Tecnologias

Python, Django, Django REST Framework, PostgreSQL e Docker Compose.

## Estrutura

- `config/`: configurações e rotas gerais do Django.
- `links/`: aplicação onde ficarão o modelo e os endpoints dos links.
- `manage.py`: comandos de gerenciamento do Django.
- `compose.yaml`: banco PostgreSQL para desenvolvimento local.

## Preparar o ambiente local

Requer Python 3.14 e Docker com Compose. Na primeira execução, crie `.env` a partir de `.env.example` e substitua `DJANGO_SECRET_KEY` e `POSTGRES_PASSWORD` por valores aleatórios. Mantenha os demais valores do exemplo para usar o PostgreSQL na porta 5432.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
docker compose config --quiet
docker compose up -d db
docker compose exec db sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
set -a
source .env
set +a
.venv/bin/python manage.py migrate
.venv/bin/python manage.py showmigrations links
```

Edite `.env` antes de iniciar o banco. O arquivo é ignorado pelo Git. Se já existir, não o substitua com `cp`. O comando `pg_isready` deve indicar que o banco aceita conexões; `showmigrations links` deve mostrar `[X] 0001_initial`.
