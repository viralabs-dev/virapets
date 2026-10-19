# ViraPets Studio — funcionalidades publicadas

Estado conferido em **19/10/2026** na [página pública](https://daneiel.github.io/virapets/), commit do site [`d61fdfb`](https://github.com/daneiel/daneiel.github.io/commit/d61fdfbb0d89c2258b7f6989172ad04f164535a3). [Deploy Pages 39257004280 concluído](https://github.com/daneiel/daneiel.github.io/actions/runs/39257004280). Esta consolidação documenta essa versão; não acrescenta funcionalidades.

## Três caminhos de criação

| Caminho | Entrega | Modelo e rede |
|---|---|---|
| Desenho procedural | Personagem estilizado original, configurado por regras | Sem modelo ou serviço de geração; processamento local |
| Foto → pixel art local | Recorte, pixelização, retoque e movimento da sua foto | Pincéis manuais sem modelo; SlimSAM local opcional para segmentação |
| Prompt completo | Texto para usar com uma plataforma de imagem escolhida pela pessoa | O site só copia/baixa o prompt; a pessoa anexa a foto na outra plataforma |

O modo foto transforma um recorte; não inventa novos olhos, bocas ou expressões. As silhuetas procedurais não são retratos fiéis de raças. Nenhum dos dois reproduz automaticamente o acabamento ilustrado de Jojo, Mel e Dara. Não há API de LLM, geração por texto, Gradio ou freellmapi integrada ao Studio.

## 12 animais, 26 combinações

| Animal | Raças, variedades ou tipos disponíveis |
|---|---|
| Cachorro | SRD, Shih-tzu, Poodle, Labrador, Pinscher |
| Gato | SRD, Siamês, Persa |
| Pato | Comum |
| Galinha | Comum |
| Pintinho | Comum |
| Coelho | Comum, Mini-lop, Angorá |
| Vaca | Holandesa, Gir, Jersey |
| Boi | Comum |
| Lhama | Comum |
| Camelo | Comum |
| Passarinho | Calopsita, Papagaio, Canário |
| Lagarto | Iguana, Lagarto, Camaleão |

Aves e répteis são apresentados como **tipos**, não como raças. As escolhas alteram silhuetas e detalhes originais; corpo, detalhes e acessório têm cores ajustáveis. Nome, ID e autoria entram na receita e no pacote. Receitas antigas sem espécie continuam como cachorro SRD. Os quatro humores são Feliz, Latindo/Chamando, Esperando e Dormindo; `barking` permanece como chave técnica para compatibilidade. Não há áudio.

[Prancha real das 26 combinações](../images/species-contact-sheet.png), produzida pelo próprio renderizador.

## Foto, seleção e animação

1. Escolha PNG, JPEG ou WebP local de até **10 MiB** e 40 megapixels. O rótulo da interface abrevia o limite como 10 MB. Uma cópia de trabalho é reduzida a até 768 pixels no lado maior. Há um desenho sintético para experimentar sem foto pessoal.
2. Recorte com pincéis manter/apagar ou ative SlimSAM. Pontos no pet incluem; pontos no fundo excluem. Use objeto inteiro/detalhe e substituir/adicionar/remover áreas, inclusive desconectadas. O modelo pode precisar de correção manual em pelos e partes pequenas.
3. Selecione Pet ou Fundo (inverso), refine a máscara com expandir/contrair/suavizar e desfaça/refaça. Escolha transparência ou preenchimento por cor. A foto de trabalho original não é pintada por essas operações.
4. Aplique a pixelização com grade 16–96, paleta 2–32 cores e contorno opcional. Retoque a arte com cor ou borracha. Reaplicar o recorte substitui os retoques.
5. Marque a cabeça na arte final 256×256, ajuste tamanho 8–100 e direção automática/esquerda/direita. A marca é necessária antes de exportar. Refazer o recorte exige marcá-la novamente.
6. Simule latido e sono. A prévia interpola movimentos; raios e Zzz acompanham a cabeça. Zzz desaparecem nos quadros 4 e 5 do despertar, contados a partir de zero. A simulação usa a arte atual ou exemplo sintético e não precisa do modelo.

[GIF real da simulação](https://daneiel.github.io/virapets/motion-demo.gif). Os efeitos são visuais, sem som ou redesenho de expressões.

## Layout e temas

Os editores ficam **abertos na página, sem modal**. O seletor e a importação de receita ficam acessíveis. No modo foto, o bloco procedural inteiro, incluindo instruções, fica oculto e inerte. Sem arte pronta, não há card Pingo vazio ou formulário de exportação. Depois de pixelizar, a única prévia/exportação compartilhada fica **dentro do editor da foto**. Alternar preserva foto, máscara, cabeça e configurações; salvar receita continua necessário antes de recarregar a página.

O botão no topo usa sol/lua, texto de ação, tooltip e nome acessível. O tema claro/escuro segue inicialmente o sistema e lembra a escolha local. Mantém os tokens BRABO e funciona por teclado; a indicação não depende só da cor.

| Captura real atual | O que comprova |
|---|---|
| [Procedural e tipos](../images/species-inline-desktop.png) | Catálogo e controles do desenho procedural |
| [Foto sem arte, desktop](../images/mode-photo-empty-1440.png) | Ausência do bloco procedural/saída vazia abaixo da foto |
| [Foto pronta, desktop](../images/mode-photo-ready-1440.png) | Prévia e exportações dentro do painel da foto |
| [Foto pronta, viewport móvel](../images/mode-photo-ready-390.png) | Organização da saída no painel estreito |
| [Sol/lua no topo](../images/species-theme-mobile.png) | Ação de tema destacada no viewport móvel |

## Modelo, privacidade e persistência

SlimSAM q8 roda em Worker no próprio navegador, com ONNX Runtime WASM CPU; não exige WebGPU. A ativação inicial envolve **36.315.496 bytes não comprimidos**, aproximadamente **36,3 MB**: 13.786.820 de pesos/configuração e 22.528.676 de runtime JS/WASM, além dos arquivos pequenos da página. Compressão e cache podem reduzir a transferência efetiva. Tamanho de download não é requisito de RAM.

O runtime é servido pelo site; os pesos vêm do Hugging Face e seus CDNs. Há requisições GET de arquivos, expondo metadados normais como IP aos hosts. A foto e os embeddings são processados localmente, sem upload da foto ou chamada de inferência paga. O cache específico guarda arquivos do modelo, não fotos. Cancelar/liberar encerra o Worker; limpar cache remove os pesos armazenados. Cache pode ser removido pelo navegador, portanto não há promessa de primeira visita offline.

A receita fotográfica guarda a pixel art derivada e a cabeça marcada. Não guarda foto original, nome do arquivo, EXIF ou máscara editável. Importar permite retocar/reanimar; recortar novamente exige selecionar a fonte. A receita ainda contém uma imagem visível do pet. A página perde os originais não salvos ao recarregar. Consulte [licenças distribuídas](https://daneiel.github.io/virapets/vendor/PHOTO-ML-NOTICES.txt).

## Exportações

| Formato | Conteúdo |
|---|---|
| PNG | Faixa RGBA 2048×256 do humor selecionado, com 8 células; não é GIF |
| ZIP | Quatro faixas PNG, `pet.json`, receita e instruções de instalação |
| JSON | Receita procedural ou arte fotográfica derivada com cabeça |
| `.wastickers` | Quatro WebPs animados 512×512, capa e metadados para importador compatível |

PNGs de foto incorporam efeitos uma vez; `sleepSigns` fica com entradas `null`. Procedural deixa os sinais de sono para o pipeline. Figurinhas de foto têm **32 quadros por humor**; procedurais têm **8**. Canvas WebP depende do navegador e pode usar compressão com perdas. O pipeline Python/Pillow oferece geração/validação local de GIFs, galeria e figurinhas. O download não instala diretamente no WhatsApp; é necessário um importador Android compatível. [Instalação e entrega do próprio pet](../../README.md#crie-seu-próprio-pet-com-sua-imagem).

## Evidências e limites reais

- **40 testes Node**: 6 core, 13 photo-core, 5 máscaras, 4 SAM, 6 espécies, 6 stickers. O cão padrão antigo foi preservado pixel a pixel.
- QA Chromium local e **na URL pública**, viewports 1440 e 390, sem erros JavaScript. Cobertura de receitas antigas/novas, teclado, tema, composição dos modos, estado, máscara, cabeça, simulação e exportações.
- A regressão da AT-024 verifica `display`, `hidden`, `inert`, retângulos, ancestralidade e unicidade de prévia/formulário, além de foco. O defeito anterior deixava a saída compartilhada fora do editor; não foi atribuído a cache.
- Pillow conferiu faixas e WebPs exportados; ZIPs passaram por `deliver`, `validate` e `build` em clones isolados, com 32 quadros no painel. Isso não implica instalação de um novo pet na sessão pessoal do Claude.
- SlimSAM real com pontos positivos/negativos e modo objeto foi testado em rodada anterior; a correção final de layout não mudou os pesos ou o protocolo do modelo.

Relatórios atuais: [espécies](../validation/species-inline-public.json), [regressão final de modos](../validation/mode-regression-public.json), [movimento e seleção](../validation/cutout-public.json), [primeira publicação do editor fotográfico](../validation/photo-editor-public.json). Os relatórios preservam seus commits e escopos históricos; não representam todos a última rodada.

**Não testados:** aparelhos físicos, Firefox/Safari e importação real no WhatsApp. Não há garantia de seleção perfeita de pelos, desempenho universal ou fidelidade artística. Animação do recorte não é geração de novas expressões.

## Exemplos e procedência

As capturas e a simulação ligadas neste guia usam desenhos sintéticos originais, identificados como exemplos de QA. Uma sessão real com foto de pug foi observada e seu pacote foi conferido localmente; a imagem não integra este repositório enquanto sua origem e permissão de republicação não forem verificadas. O nome de autoria padrão de uma receita não comprova a autoria da foto.

## Onde estão os arquivos

- [Plugin, pipeline Python e documentação](https://github.com/viralabs-dev/virapets): usar para entregar e instalar pets.
- [Arquivos públicos do Studio](https://github.com/daneiel/daneiel.github.io/tree/d61fdfbb0d89c2258b7f6989172ad04f164535a3/virapets): usar para estudar ou servir o site estático.
- O repositório do plugin não recebe automaticamente todos os commits locais de desenvolvimento do Studio. Publicação de site, documentação e instalação são operações separadas.
