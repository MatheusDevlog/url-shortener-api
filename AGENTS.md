# Guia técnico para agentes de desenvolvimento

## Fontes e escopo

- Este repositório contém um MVP concluído de encurtamento de URLs. Consulte `README.md` para o contrato público e os comandos de execução antes de propor mudanças.
- Quando existirem, leia `docs/CONTEXTO_DESENVOLVIMENTO.md` para preferências privadas de colaboração e `docs/ESTADO_URL_SHORTENER.md` para o estado confirmado. Os arquivos em `docs/` não fazem parte do repositório público.
- Inspecione o código e o estado atual do Git; não deduza que uma funcionalidade futura, um deploy ou uma verificação anterior se aplicam a uma nova alteração.
- Mantenha mudanças pequenas e relacionadas ao pedido. Preserve o comportamento existente quando ele não for parte da tarefa.

## Arquitetura e contrato

- A aplicação usa Django 5.2, Django REST Framework e PostgreSQL. `compose.yaml` inicia somente o banco; a API e os testes executam no Python local da `.venv`.
- `config/settings.py` lê as variáveis do processo; `config/urls.py` distribui as rotas gerais. `links/urls.py` conecta as rotas da API às views em `links/views.py`.
- `links/models.py` define o único model próprio, `Link`, com URL original, código único, contador de acessos e data de criação. Alterações de esquema exigem uma migration em `links/migrations/`.
- `links/serializers.py` valida a entrada e representa o link. A criação aceita URL HTTP ou HTTPS, gera um código de oito caracteres e tenta novamente em caso de colisão, até cinco tentativas. O banco garante a unicidade; a resposta calcula `short_url` a partir da requisição.
- `GET` e `POST /api/links/` listam e criam links. `GET` e `DELETE /api/links/<code>/` consultam e excluem pelo código. `GET /<code>/` redireciona para a URL original e soma um acesso.
- A listagem não tem paginação. Consultas de dados não incrementam o contador; ele mede requisições GET à URL curta, não visitantes únicos. Mantenha os caminhos com barra final e confira os status HTTP documentados no README.

## Convenções de implementação

- Use os recursos existentes do Django e do DRF antes de acrescentar abstrações ou dependências. Mantenha validação de entrada, persistência e resposta nos pontos já responsáveis por cada etapa.
- A criação trata `IntegrityError` depois de sair de `transaction.atomic()`, para poder consultar o banco e repetir somente uma colisão de código. Preserve essa ordem ao alterar a regra.
- O redirecionamento incrementa o contador com `F()` no banco e responde 302 com instruções contra cache. Preserve o destino e os parâmetros da URL original.
- Não suponha que alterar uma view exige migration. Crie migrations quando o esquema dos models mudar e revise o arquivo gerado antes de aplicá-lo.
- Atualize o README quando modificar o contrato HTTP ou a forma real de executar o projeto.

## Segurança e dados locais

- Todos os endpoints do MVP são públicos, inclusive DELETE. Não descreva esses endpoints como protegidos por autenticação ou prontos para uso público irrestrito.
- O `csrf_exempt` está limitado à função pública de redirecionamento, que aceita somente GET; o middleware CSRF global permanece ativo. Não amplie essa isenção sem analisar o impacto.
- Preserve `.env`, `.venv/` e `docs/` fora do versionamento. Use `.env.example` apenas como modelo e não publique segredos nem dados privados em código, documentação ou PRs.
- O código não verifica se o site de destino está disponível ou é confiável. Não atribua ao validador de URL garantias que ele não fornece.

## Verificação

- Acrescente ou ajuste testes de comportamento em `links/tests/` quando modificar funcionalidades. Cubra o fluxo principal, entradas inválidas, recursos inexistentes e efeitos no banco pertinentes à alteração.
- Os testes usam pytest e pytest-django, configurados em `pytest.ini`. Com o PostgreSQL iniciado e as variáveis do `.env` carregadas no ambiente, execute `.venv/bin/python -m pytest -q`.
- `manage.py check`, `makemigrations --check --dry-run` e `showmigrations` ajudam a verificar configuração e esquema, mas não substituem os testes de comportamento.
- Em mudanças de endpoint, confira também uma requisição HTTP representativa e os efeitos esperados. Registre separadamente o que foi executado, o que foi informado por outra pessoa e o que permanece sem verificação.

## Git e entrega

- `main` é a branch principal. Desenvolva mudanças em branches de trabalho, revise o diff e os testes antes do commit e abra PR para integrar uma entrega concluída.
- Commits e PRs devem representar mudanças reais. A descrição do PR deve relatar alterações e verificações efetivas, sem prometer trabalho não realizado.
- Não faça commit, push, merge ou publicação sem a autorização aplicável. Verifique o estado antes de orientar comandos que dependam da branch ou do remoto.
