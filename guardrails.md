---

### Passo B — Atualizar o `GUARDRAILS.md`

Crie também o arquivo `GUARDRAILS.md`:

```markdown
# GUARDRAILS.md — Segurança do Sistema

## Princípios de Segurança

1. **Menor privilégio** — agente acessa só o necessário
2. **Filtrar entrada** — todo input do usuário é validado
3. **Mascarar saída** — dados sensíveis nunca aparecem crus
4. **Nunca credenciais no código** — sempre via .env

## Ameaças Conhecidas

### 1. Prompt Injection
**Risco:** Usuário tenta manipular o Gemini via input
**Proteção:** guardrails.py → filtrar_entrada()
**Teste:** test_guardrails.py → test_injection_*

### 2. Dados Sensíveis na Saída  
**Risco:** CPF, emails, dados pessoais aparecem na tela
**Proteção:** guardrails.py → filtrar_saida()
**Teste:** test_guardrails.py → test_dados_sensiveis_*

### 3. Input Malicioso
**Risco:** SQL injection, caracteres especiais
**Proteção:** guardrails.py → validar_municipio()
**Teste:** test_guardrails.py → test_input_malicioso_*

## O que NUNCA deve aparecer na interface
- Chaves de API
- Nomes completos de pessoas físicas  
- CPF ou dados bancários
- Stack traces completos de erro
- Queries SQL brutas

## Checklist antes de cada deploy
- [ ] Todos os testes de guardrails passando
- [ ] .env não está commitado
- [ ] Nenhuma chave hardcoded no código
- [ ] Mensagens de erro são amigáveis (sem detalhes técnicos)