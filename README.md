# URL Shortener API

API para criar links curtos e redirecionar para as URLs originais. O projeto está na etapa de estrutura inicial; os endpoints ainda não foram implementados.

## Tecnologias

Python, Django, Django REST Framework e PostgreSQL.

## Estrutura

- `config/`: configurações e rotas gerais do Django.
- `links/`: aplicação onde ficarão o modelo e os endpoints dos links.
- `manage.py`: comandos de gerenciamento do Django.

## Preparar o ambiente local

Requer Python 3.14 e um servidor PostgreSQL. A configuração do banco usa as variáveis `POSTGRES_*` do arquivo `.env.example`.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
set -a
source .env
set +a
.venv/bin/python manage.py check
```

Edite os valores de `.env` para corresponder ao seu banco local. O arquivo `.env` é ignorado pelo Git. Os comandos de execução ainda precisam ser verificados em um ambiente com as dependências instaladas.
