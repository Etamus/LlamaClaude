# OpenClaude (fork llama.cpp-only)

> **Este projeto é um fork do OpenClaude, baseado na versão v0.2.3, adaptado para funcionar exclusivamente com modelos locais no formato GGUF via llama.cpp.**

---

## Sobre o Projeto

Este projeto é uma CLI de agente de código totalmente open-source, baseada no OpenClaude v0.2.3, mas **não utiliza mais nenhuma API externa**. Toda a inferência é feita localmente, utilizando apenas o [llama.cpp](https://github.com/ggerganov/llama.cpp) e modelos no formato GGUF.

- Não há integração com OpenAI, Gemini, Ollama, Codex, ou qualquer outro provedor externo.
- Nenhuma chave de API é necessária.
- Todo o processamento é feito localmente, garantindo privacidade e independência de serviços de terceiros.
- Suporte apenas a modelos GGUF compatíveis com o llama.cpp.

## Instalação

1. **Pré-requisitos:**
   - Tenha o [llama.cpp](https://github.com/ggerganov/llama.cpp) instalado e funcional em seu sistema.
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

## Licença

Este projeto segue a licença MIT, conforme o arquivo [LICENSE.txt](LICENSE.txt).

## Créditos e Origem

Este fork foi criado a partir do [OpenClaude](https://github.com/Gitlawb/openclaude), versão v0.2.3, removendo toda dependência de APIs externas e focando exclusivamente em execução local com llama.cpp.

---
