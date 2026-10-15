# jojo

Um cachorro em pixel art no painel do Claude Code que mostra, de relance, o que o Claude está fazendo:

| Humor | Quando |
|---|---|
| **HAPPY** | o Claude terminou uma resposta (por 6 s) |
| **BARKING** | o Claude precisa de você: pedido de permissão, pergunta (`AskUserQuestion`) ou plano (`ExitPlanMode`) |
| **WAITING** | o Claude está trabalhando, e em repouso |

## Autor

Daniel Souza ([@daneiel](https://github.com/daneiel)).

## Instalar

No prompt do Claude Code (terminal):

```text
/plugin install jojo --marketplace viralabs-dev/claude-mods
```

O mesmo mod sai direto deste repositório, sem o catálogo: `/plugin install jojo --marketplace viralabs-dev/jojo`.

Responda `y` para adicionar o marketplace e escolha o escopo de usuário. Vale a partir da próxima sessão (ou depois de `/reload-plugins`).

## Para que serve

Saber, sem ler a conversa, se o Claude terminou, se espera por você ou se ainda trabalha. O desenho são 43×20 células de meio-bloco (`▀`) coloridas, lidas na grade da própria pixel art da folha de sprites (3 humores × 4 quadros), e precisa de um terminal com cor de 24 bits. Fora do terminal (desktop, VS Code, celular) o painel mostra só o rótulo do humor.

O painel lateral abre sozinho em janelas largas (de 110 a 144 colunas, conforme o motor); abaixo disso, `/jojo` abre. Com o plugin [Flightdeck](https://github.com/scasella/claude-flightdeck) instalado, o Jojo é desenhado no fundo do painel dela, e o painel próprio fecha.

## Exemplos (telas reais)

Capturas do Claude Code 2.1.300.

### Embaixo da Flightdeck

![O Jojo feliz embaixo do painel Flightdeck](docs/capturas/01-embaixo-da-flightdeck.png)

## Comandos

| Comando | O que faz |
|---|---|
| `/jojo` | abre o painel do Jojo (ou avisa que ele está embaixo da Flightdeck) |

## Capacidades usadas

Saída de `claude plugin validate .`:

- Eventos: `session.start`, `command.run` (`/jojo`), `turn.start`, `turn.complete`, `tool.call`, `classic.PermissionRequest`, `classic.Notification`, `ui.render` dos painéis `jojo` e `flightdeck`.
- `tool.call`, `classic.PermissionRequest` e `classic.Notification` só **observam**: todo hook repassa o evento intacto com `next(e)` e nunca muda nem barra uma ferramenta; uma falha do mod ao gravar o humor é engolida.
- `$.state` (`jojo.mood`): o humor mostrado.
- `$.clock.every`, `$.ui.blit`: a animação, que troca só as células do desenho a cada quadro.
- `$.command.register`, `$.ui.open`, `$.ui.close`, `$.ui.resolve`: o comando e o painel.

Nenhuma capacidade sensível: não usa processo, rede, arquivos, modelos nem MCP, e não lê prompt nem o conteúdo das chamadas de ferramenta.

## Configuração

Nenhuma por pessoa. No código: `HAPPY_MS` e `FRAME_MS` em `hooks/mood.ts` (quanto dura o HAPPY e o ritmo de cada animação).

## Dependências de sistema

Nenhuma para usar. Para regenerar os quadros a partir da folha de sprites: Python 3 com Pillow (`python3 tools/build_frames.py`, que escreve `hooks/frames.ts`).

## Limites conhecidos

- Onde uma organização gerencia o Claude Code, `classic.PermissionRequest` e `classic.Notification` não rodam em plugins instalados pela pessoa: lá o Jojo só late nas perguntas e nos planos.
- Instalado depois da Flightdeck, o Jojo abre numa aba própria ao lado dela, e não embaixo. A Flightdeck desenha o próprio painel sem passar a vez; a causa provável (ainda não confirmada) é a ordem em `enabledPlugins` no `~/.claude/settings.json`, em que o plugin que vem antes fica por fora. Pôr o Jojo antes da Flightdeck deve resolver.
- A folha de sprites (`assets/jojo-sprites.jpeg`) foi gerada por IA; a licença dela está em revisão antes de o repositório ficar público.

## Como remover

```text
claude plugin uninstall jojo@viralabs-mods     # instalado pelo catálogo
claude plugin uninstall jojo@viralabs-jojo     # instalado direto deste repositório
```

## Versão do Claude Code validada

2.1.300, no Linux.
