# jojo-mod

Mods experimentais do Claude Code da viralabs. Cada mod é uma pasta; a raiz é um marketplace (`viralabs-claude-mod`).

- `jojo/` — um cachorro em pixel art num painel (ou embaixo da Flightdeck): HAPPY quando o Claude termina uma resposta, BARKING quando precisa de você, WAITING enquanto trabalha e em repouso.

## Instalar

Dentro do Claude Code:

```
/plugin marketplace add viralabs-dev/jojo-mod
/plugin install jojo@viralabs-claude-mod
```

Ou pela linha de comando:

```bash
claude plugin marketplace add viralabs-dev/jojo-mod
claude plugin install jojo@viralabs-claude-mod --scope user
```

O desenho precisa de um terminal com cor de 24 bits. O painel abre sozinho em janelas largas; em janelas estreitas, `/jojo` abre.

## Desenvolver

```bash
claude plugin validate jojo
claude plugin test jojo
python3 jojo/tools/build_frames.py   # regenera jojo/hooks/frames.ts (precisa do Pillow)
```

A folha de sprites (`jojo/assets/jojo-sprites.jpeg`) foi gerada por IA. A licença dela ainda está em revisão antes de o repositório ficar público.
