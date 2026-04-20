# LlamaClaude

O LlamaClaude é uma adaptação técnica do OpenClaude (v0.2.3), reestruturada para transformar o agente de código original em uma solução de inferência totalmente local. Enquanto o projeto base contava com suporte a provedores de nuvem, o LlamaClaude removeu integralmente qualquer dependência de APIs externas. A arquitetura foi adaptada para rodar exclusivamente através do motor llama.cpp, utilizando modelos no formato GGUF para garantir máxima performance e soberania de dados. Esta versão mantém a estrutura e as funcionalidades de agente de código do OpenClaude v0.2.3, mas redefine o seu funcionamento central: agora, todo o processamento ocorre offline no seu hardware, eliminando custos, latência de rede e riscos de privacidade.

---

<img width="1092" height="553" alt="{CDDBEB63-B306-4869-8CC4-EDB25146014B}" src="https://github.com/user-attachments/assets/80e865c7-5423-45a3-9927-656071088280" />

---

## Sobre o Projeto

Este projeto é uma CLI de agente de código totalmente open-source, baseada no OpenClaude v0.2.3, mas **não utiliza mais nenhuma API externa**. Toda a inferência é feita localmente, utilizando apenas o [llama.cpp](https://github.com/ggerganov/llama.cpp) e modelos no formato GGUF.

- Não há integração com OpenAI, Gemini, Ollama, Codex, ou qualquer outro provedor externo.
- Nenhuma chave de API é necessária.
- Todo o processamento é feito localmente, garantindo privacidade e independência de serviços de terceiros.
- Suporte apenas a modelos GGUF compatíveis com o llama.cpp.

## Instalação

1. **Pré-requisitos:**
   - Tenha o [llama.cpp](https://github.com/ggerganov/llama.cpp) instalado no projeto.
   - Baixe um modelo GGUF de sua preferência e coloque na pasta `models/`.

2. **Instale as dependências do projeto:**

```bash
bun install
```

3. **Build do projeto:**

```bash
bun run build
```

4. **Inicie a CLI:**

```bash
node dist/cli.mjs
```

## Como Usar

- Todos os comandos e fluxos são executados localmente.
- Para trocar de modelo, basta substituir o arquivo GGUF na pasta `models/` e ajustar a configuração se necessário.
- Não há necessidade de configurar variáveis de ambiente de API.

## Estrutura do Repositório

- `src/` - Código-fonte principal da CLI
- `scripts/` - Scripts de build e manutenção
- `docs/` - Documentação
- `python/` - Utilitários Python auxiliares
- `models/` - Modelos GGUF para uso com llama.cpp
- `bin/` - Entrypoints e utilitários
- `vscode-extension/openclaude-vscode/` - Extensão para VS Code

## Aviso Legal

O LLamaClaude é baseado no projeto OpenClaude, que é comunitário independente e não é afiliado, endossado ou patrocinado pela Anthropic. O OpenClaude originou-se da base de código do Claude Code e, desde então, foi substancialmente modificado para suportar múltiplos provedores e uso aberto. "Claude" e "Claude Code" são marcas registradas da Anthropic PBC.