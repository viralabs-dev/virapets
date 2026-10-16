# Pets no Claude Code

As gravações `*-no-claude-0.4.0.gif` mostram Jojo HAPPY, Mel BARKING e Dara SLEEPING na instalação local ViraPets 0.4.0, com Flightdeck 0.4.0 e Claude Code 2.1.301. Os PNGs de mesmo nome são quadros estáticos das gravações.

Captura em 15/10/2026, a partir do código `96131a71f34fef723271db9c69fdede4ee40e8f3`. Uma sessão real do CLI foi aberta em PTY de 150×48 células, usando a instalação de usuário, sem `--plugin-dir`. Os comandos `/virapets jojo happy`, `/virapets mel barking` e `/virapets dara sleeping` foram executados localmente; nenhum prompt foi enviado ao modelo.

A saída ANSI foi renderizada com pyte/Pillow em 1200×768, usando células de 8×16 pixels e amostragem de 80 ms. Portanto, são gravações do terminal renderizadas, não capturas nativas da área de trabalho. O GIF da Dara inclui cochilo, despertar e retorno ao sono, com o ZzZ desaparecendo durante o despertar. A configuração de fonte e o tamanho da janela podem alterar a aparência em outro terminal.

[Metadados, intervalos e hashes](recording-0.4.0.json). Os GIFs dos personagens apresentados no README continuam sendo os originais em `assets/pets/<id>/animations/`; nenhuma arte ou configuração do painel foi alterada para estas gravações.

`01-embaixo-da-flightdeck.png` é a captura histórica do Jojo 0.2.0 e permanece como referência, sem representar a instalação atual.

## Privacidade das capturas

Revisadas em 16/10/2026: caminhos locais, plano da conta, métricas de uso/custo/contexto e controles de sessão foram ocultados com máscaras opacas em todos os quadros. A captura histórica também omite branch, mensagem e indicadores da sessão. Os personagens, a quantidade de quadros e os tempos das animações foram preservados. Os hashes descrevem os arquivos revisados.

A revisão abrange os arquivos atuais; commits anteriores podem conservar as versões originais. Antes de acrescentar uma captura, conferir todos os quadros e remover informações de conta, caminhos, prompts privados, credenciais e metadados pessoais.

Também foram removidos os perfis APP1 de duas pranchas de referência em `assets/pets/`, preservando os pixels. Relatórios históricos de validação mantêm os hashes da época em que foram executados.
