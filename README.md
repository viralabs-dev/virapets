# ViraPets

Pets em pixel art que acompanham o Claude Code. Jojo, Mel e Dara compartilham o mesmo painel, eventos e relógio; cada personagem tem suas próprias imagens e tempos.

| Pet | Identidade | Estado da arte |
|---|---|---|
| Jojo | cão caramelo, contorno preto e olhos caramelo | arte aprovada, preservada da versão 0.2.0 |
| Mel | Shih Tzu creme, orelhas caídas e um dentinho inferior esquerdo | primeira versão para revisão visual |
| Dara | cadela clara e castanha, óculos, bandana vermelha e orelhas assimétricas | primeira versão para revisão visual |

Abra `assets/animation-virapets.html` para ver os 12 GIFs, com fundo claro/escuro e downloads incorporados. A galeria funciona sem servidor.

## Comandos

```text
/virapets jojo
/virapets mel happy
/virapets dara barking
/virapets mel waiting
/virapets dara sleeping
/virapets list
```

`/virapets` abre o pet atual; sem humor, a seleção conserva o humor atual. `/jojo [happy|barking|waiting|sleeping]` continua como atalho para Jojo. Nomes ou humores inválidos mostram a ajuda sem mudar a seleção. Os comandos não chamam o modelo. Esc devolve o foco ao prompt.

| Humor | Quando |
|---|---|
| HAPPY | resposta principal concluída; volta a WAITING em 6 s |
| BARKING | permissão, pergunta AskUserQuestion ou plano ExitPlanMode |
| WAITING | turno ativo ou início de repouso |
| SLEEPING | 30 s de repouso, idle_prompt ou turno encerrado por erro de API |

Os eventos automáticos continuam após a escolha manual. Um turno novo acorda o pet; um turno longo não conta como inatividade. Erro de API pode incluir falta de créditos, mas o plugin não consulta saldo. Respostas de subagentes não mudam o humor.

## Instalação e migração

A versão 0.3.2 é a evolução do plugin Jojo. A renomeação do repositório, a publicação do código e a atualização da instalação são etapas distintas. Estes comandos de marketplace dependem da publicação da versão nova:

```text
/plugin install virapets --marketplace viralabs-dev/claude-mods
```

Também é possível instalar diretamente:

```text
/plugin install virapets --marketplace viralabs-dev/virapets
```

Antes de ativar ViraPets, desative o plugin antigo `jojo@viralabs-mods` (ou `jojo@viralabs-jojo`) para não carregar dois painéis e dois comandos `/jojo`. A escolha começa em Jojo/WAITING; a chave antiga `jojo.mood` não é migrada. Depois, use `/reload-plugins` ou abra outra sessão. O estado `virapets.selection` preserva pet e humor nas recargas do módulo.

Para instalar o clone local sem publicar: `claude plugin install virapets --marketplace /caminho/do/clone/virapets --scope user`. Essa instalação usa `virapets@viralabs-virapets`; desative o antigo `jojo@viralabs-mods` e mantenha ViraPets antes da Flightdeck em `enabledPlugins`.

Para desenvolvimento local, carregue a pasta com `claude --plugin-dir .`. Para um teste isolado da configuração instalada: `claude --plugin-dir . --setting-sources '' --strict-mcp-config`.

Remoção: `claude plugin uninstall virapets@viralabs-mods` (catálogo) ou `virapets@viralabs-virapets` (direto).

## Organização

```text
assets/pets/<id>/
  pet.json                 identificação, tempos e ZzZ por quadro
  sprites/<humor>.png       faixas editáveis, células quadradas
  animations/<humor>.gif    fonte dos quadros e tempos do painel
  animations/animations.json
  references/              referência e prompts da arte
assets/animation-virapets.html
generated/catalog.ts       catálogo compilado; não editar
generated/pets/<id>/frames*.ts
hooks/                     eventos, seleção, relógio e layout
tools/pets.py             entrada única da ferramenta
tools/virapets/            módulos compartilhados
tools/tests/              testes do pipeline Python
tests/                     testes no motor Claude Code
```

`hooks/pets.ts` resolve a seleção e valida comandos. `hooks/mood.ts` mantém as regras dos humores. `hooks/animation.ts` avança conforme os tempos do pet; `hooks/layout.ts` escolhe o tamanho que cabe. `hooks/register.tsx` conecta tudo ao Claude e à Flightdeck. Adicionar arte não exige copiar esses módulos.

## Criar e manter pets

Requer Python 3 e Pillow somente para gerar assets (`python3 -m pip install -r tools/requirements.txt`; validado com Pillow 12.3.0). O runtime instalado não depende de Python. Os comandos são executados na raiz:

```sh
python3 tools/pets.py list
python3 tools/pets.py new --pet luna --name Luna
# Adicione happy.png, barking.png, waiting.png e sleeping.png em assets/pets/luna/sprites/
python3 tools/pets.py gifs --pet luna
python3 tools/pets.py build
python3 tools/pets.py validate
```

`new` não sobrescreve um pet existente. Cada faixa tem N quadros quadrados na horizontal, fundo transparente e lado mínimo de 48 pixels; os pets atuais usam 8 quadros de 256×256. Mantenha escala, margens e ponto de apoio entre poses. Ajuste `timings` e `sleepSigns` de `pet.json` ao número de quadros. `status` é `draft` ou `ready`, exclusivamente para informar a revisão visual.

`timings` contém uma lista por humor, em milissegundos (mínimo 20). `sleepSigns` tem um item por quadro sleeping: `null` quando acorda, ou `["ZzZ", deslocamentoHorizontal, posiçãoVertical]`; aceita letras z/Z, até três, e posição vertical 0 ou 1. A arte PNG não deve conter ZzZ, que é composto pelo pipeline.

`gifs` exporta apenas o pet escolhido, ou todos se omitido. **Não execute gifs no Jojo para apenas compilar o runtime:** seus GIFs aprovados já estão prontos. `build` lê os GIFs, gera as escalas Raster configuradas por pet e atualiza o catálogo e a galeria. `build --pet mel` recompila só Mel; pets ainda sem GIFs ficam fora da compilação e galeria, e só entram no catálogo após terem frames gerados. `validate` confere todos, inclusive pastas incompletas. `gallery --output caminho.html` recria somente a galeria.

`effects` é opcional: `{"happy":"sparkles","barking":"bark"}` acrescenta brilhos e traços dourados sincronizados às poses, sem repintar ou diminuir o pet. Mel e Dara usam essa camada; Jojo conserva os efeitos da arte aprovada. As cores douradas têm entradas próprias na paleta GIF para não se confundirem com o pelo.

`rendering` configura somente a redução para o terminal. O perfil padrão `outlined` e as seis escalas originais permanecem em Jojo e Mel. Dara usa `detailed`, que preserva as cores internas dos óculos e da bandana e reforça apenas a borda externa. Uma paleta compartilhada de até 65 cores reduz as combinações de estilos por pose no Raster; suas escalas extras 28, 36, 42, 44 e 46 aproveitam melhor painéis estreitos, inclusive em monitor Full HD na vertical. `sizes` deve conter números pares ordenados entre 8 e 48 e terminar em 48. GIFs, sprites e figurinhas permanecem iguais.

Os GIFs são a fonte canônica de quadros e tempos do painel. Para substituir um GIF pronto, mantenha os quatro tamanhos iguais, transparência, loop infinito e contagens coerentes com o manifesto; rode `build`. O tempo efetivo vem do GIF, enquanto `timings` configura a próxima exportação dos PNGs. O GIF arredonda limites acumulados em passos de 10 ms para evitar deriva.

Os módulos Python separam catálogo/validação (`catalog.py`), composição/paleta GIF (`gifs.py`), leitura/redução (`raster.py`), codificação do terminal (`frames.py`), letras (`sleep.py`), galeria (`gallery.py`), efeitos (`effects.py`) e figurinhas (`stickers.py`). A geração antiga por `build_frames.py`, `slice_frames.py` e `build_gifs.py` foi substituída pela CLI única.

## Figurinhas para WhatsApp

Cada pet tem um pacote único em `assets/pets/<id>/stickers/<id>-animado.wastickers`, com HAPPY, BARKING, WAITING e SLEEPING. O pacote do Jojo foi preservado. Para os novos pets, `python3 tools/pets.py stickers --pet mel` e `--pet dara` exportam WebP animado, transparente, 512×512 e verificam a composição e os tempos.

No Android, abra o arquivo `.wastickers` em um aplicativo compatível com esse formato e use a opção de adicionar o pacote ao WhatsApp. Pacotes existentes são preservados; use `--force` para reexportar após alterar um GIF. A exportação é validada localmente; a importação no aparelho depende do aplicativo e não foi testada aqui. Arrastar um WebP animado para o WhatsApp Web não equivale a importar o pacote.

## Aparência e limites

O Claude desenha o pet em Raster de meio-blocos, em larguras de 8 a 48 pixels, conservando margens laterais. A redução preserva traços escuros; as poses não são misturadas. O ZzZ é removido do GIF por sua cor reservada e reconstruído em pixels, acima da cabeça, sem depender da fonte. No menor tamanho, as letras são compactadas para não cobrir personagens altos. O personagem não encolhe para acomodá-las.

Use terminal True Color; o host ainda quantiza cores em passos de 17. A galeria tem resolução maior que o terminal. Painéis abaixo de 10 colunas e superfícies não terminais mostram somente o humor.

Com Flightdeck, o pet fica no fundo do painel dela. ViraPets precisa preceder Flightdeck na ordem `enabledPlugins`, pois a Flightdeck pode responder sem passar o render ao próximo hook; na ordem inversa, o pet fica em painel próprio. A geometria da tela também limita a altura disponível.

No SLEEPING da Dara, os óculos deslizam até a ponta do nariz enquanto a cabeça tomba; no susto, a boca abre e os óculos voltam à posição normal. O ZzZ desaparece nos quadros do despertar. Uma orelha permanece ereta e a outra abaixada.

No SLEEPING da Mel, o despertar traz um olhar desconfiado de canto, com o branco dos olhos mais visível. Só o dente inferior esquerdo da cachorra fica para fora (à direita de quem olha a imagem).

## Capacidades

Eventos: session.start, command.run, turn.start/complete, tool.call, classic.PermissionRequest/Notification e ui.render. Usa estado `virapets.selection`, relógio, registro de comando, abertura/fechamento de painel e ui.blit. Não usa processo, rede, arquivos, modelo ou MCP no runtime; não lê o conteúdo de prompt nem de chamadas de ferramenta. Hooks de passagem repassam o evento intacto, e falhas ao gravar estado são absorvidas.

Em instalações gerenciadas por organização, os hooks clássicos de plugins pessoais podem não rodar; perguntas e planos continuam acionando BARKING.

## Validação

```sh
claude plugin validate .
claude plugin test .
PYTHONPATH=tools python3 -m unittest discover -s tools/tests -v
```

Além da suíte, confira a galeria, as quatro poses de cada pet no Claude real, a troca de personagem e a composição com Flightdeck. `docs/capturas/01-embaixo-da-flightdeck.png` preserva a evidência histórica do Jojo 0.2.0; não é prova da nova versão.

## Autor e licença

Daniel Souza ([@daneiel](https://github.com/daneiel)). [MIT](LICENSE), para código e assets. As referências foram geradas por Gemini e as novas faixas foram criadas com a ferramenta de imagem do Codex. Prompts ficam em `assets/pets/<id>/references/`. Imagens sem garantia de direitos de terceiros.
