# DEPLOY.md — Verba na Minha Cidade

## Checklist pré-deploy

- [ ] Todos os testes passando: `pytest tests/ -v`
- [ ] CI verde no GitHub Actions
- [ ] `.env` **não** commitado (verificar `git status`)
- [ ] `secrets.toml` **não** commitado (verificar `git status`)
- [ ] `*.json` (service account) **não** commitado
- [ ] `requirements.txt` atualizado e sem dependências dev

---

## Variáveis de ambiente necessárias

### Streamlit Cloud → Settings → Secrets
Cole o conteúdo gerado por `python scripts/format_secrets.py`:

```toml
[gcp]
project_id = "treinamento-sql-342216"
gemini_api_key = "SUA_CHAVE_AQUI"

[gcp.service_account]
type = "service_account"
project_id = "treinamento-sql-342216"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "...@treinamento-sql-342216.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

### GitHub Actions → Settings → Secrets and variables → Actions
| Secret | Valor |
|--------|-------|
| `GCP_PROJECT_ID` | `treinamento-sql-342216` |
| `GEMINI_API_KEY` | sua chave Gemini |

---

## Deploy no Streamlit Cloud (passo a passo)

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. **New app** → conectar repositório `oseasjnr27/verba-na-minha-cidade`
3. Branch: `main` | Main file: `app.py`
4. **Advanced settings** → colar o `secrets.toml` gerado
5. Clique **Deploy**
6. Aguardar instalação (~3-5 min)

---

## Gerar secrets.toml localmente

```bash
venv\Scripts\activate
python scripts/format_secrets.py
# Arquivo gerado em: .streamlit/secrets.toml
```

---

## Erros comuns e soluções

### "Error installing requirements"
**Causa mais comum:** dependência incompatível com Linux.
**Solução:**
```bash
# Verificar se requirements.txt instala limpo
pip install -r requirements.txt --dry-run
# Remover pacotes Windows-only (ex: win32_setctime)
# Remover pacotes não usados (ex: reflex, redis, grip)
```

### "Cannot parse as CloudRegion"
**Causa:** `GCP_PROJECT_ID` incorreto nos secrets.
**Solução:** Verificar se o valor em `[gcp] project_id` é exatamente `treinamento-sql-342216` (sem espaços ou caracteres extras).

### "Invalid credentials" / "403 Forbidden"
**Causa:** Service account sem permissão no BigQuery.
**Solução:**
1. Acessar [console.cloud.google.com](https://console.cloud.google.com) → IAM
2. Confirmar que a service account tem papel `BigQuery Data Viewer` + `BigQuery Job User`

### "ModuleNotFoundError"
**Causa:** Pacote faltando no `requirements.txt`.
**Solução:** Adicionar o pacote com versão fixada e fazer push.

---

## Rollback

```bash
# Ver commits recentes
git log --oneline -10

# Reverter para commit anterior
git revert HEAD
git push origin main

# Streamlit Cloud faz redeploy automaticamente após o push
```

---

## Verificação pós-deploy

- [ ] App carrega sem erro na URL pública
- [ ] Busca de município funciona (ex: "Muriaé")
- [ ] Gráficos renderizam corretamente
- [ ] Chat com Vera responde
- [ ] Tema dark aplicado
