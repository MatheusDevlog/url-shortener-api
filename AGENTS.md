# Instruções para agentes de desenvolvimento

## Contexto e retomada

- No início da sessão, leia `docs/CONTEXTO_DESENVOLVIMENTO.md` e `docs/ESTADO_URL_SHORTENER.md`, quando existirem, antes de alterar arquivos.
- Esses documentos são privados e ficam ignorados pelo Git. Não copie seu conteúdo pessoal para documentação pública, commits ou PRs.
- Se não estiverem disponíveis, siga este arquivo, consulte o README e inspecione o código. Não presuma o estado da branch, do PR ou das verificações.
- As orientações atuais do usuário prevalecem sobre as regras destes documentos.

## Colaboração

- Responda em português brasileiro e ajuste as explicações às dúvidas apresentadas.
- Antes de implementar uma parte importante, explique objetivo, arquivos envolvidos e caminho da informação pelo sistema.
- Trabalhe em uma funcionalidade por vez, mantendo código simples, legível e escopo pequeno.
- Após editar arquivos, explique por arquivo o que mudou, como foi feito, por que existe e como se conecta ao restante do projeto.
- Use linguagem natural e exemplos concretos de uso da API nas explicações de funcionalidades. Relacione a situação real ao caminho da requisição, ao código de cada arquivo e aos efeitos nos dados; explique os termos necessários com detalhe proporcional à mudança.
- O usuário executa comandos de desenvolvimento, instalação, migração, testes, Git e GitHub, salvo pedido explícito para executá-los. A IA pode ler e editar arquivos.
- Ao orientar comandos, informe onde executar, para que servem e o resultado esperado. Peça a saída apenas em caso de erro, diferença ou dúvida.
- Indique claramente a próxima ação. Se houver dúvida sobre o código, esclareça antes de avançar.
- Ao sugerir novas ferramentas, skills ou ajustes no fluxo de trabalho, explique o motivo e o impacto para o usuário avaliar antes de adotá-los. Continue o trabalho já combinado que não depende dessa decisão.
- Ao receber uma nova regra de trabalho, pergunte se ela deve ser registrada no contexto, exceto quando o usuário já pedir o registro. Mantenha este arquivo coerente com as regras essenciais aprovadas.

## Verificação

- Implemente testes automatizados relevantes junto da funcionalidade, antes do commit. Verifique sucesso, entradas inválidas e regras importantes; não deixe toda a suíte para o final.
- O projeto usa pytest e pytest-django. Oriente a execução de `.venv/bin/python -m pytest -q` com o PostgreSQL iniciado e as variáveis do `.env` carregadas pelo usuário.
- `manage.py check` e migrations são verificações complementares; não substituem testes de comportamento.
- Use Thunder Client como padrão para testes manuais de endpoints. Forneça método, URL, cabeçalhos/autenticação necessários, corpo, status e resposta esperados, incluindo efeitos nos dados quando aplicáveis.
- Testes manuais complementam os automatizados, sem exigir repetição de toda a suíte. Use curl nas orientações manuais somente por solicitação ou necessidade específica de documentação.
- Relate com precisão o que foi executado, o que foi confirmado pelo usuário e o que está pendente.

## Git e entrega

- Use `main` como branch principal; branches de trabalho e mensagens de commit em português. Prefixos como `feat`, `fix`, `test`, `docs` e `chore` podem continuar em inglês.
- Use `git pull` como padrão para atualizar branches que acompanham o remoto. Se houver divergência ou conflito, analise antes de continuar.
- Siga o fluxo: implementar, testar, revisar, commit, push da branch, PR, revisão e merge. Não invente histórico nem publique verificações não realizadas.
- Ao orientar um PR, forneça título, descrição pronta, branch de origem e branch de destino.
- A descrição do PR deve conter alterações e verificações da entrega. Não inclua próximas etapas ou planos futuros; mantenha-os na conversa ou no estado privado do projeto.
- Preserve `.env` e `docs/` fora do versionamento. Não exponha valores secretos nas explicações.
