# Personagens sem LLM — referência e evolução

**Estado atual publicado:** o Studio oferece 12 animais e 26 combinações procedurais, além de recorte/pixelização/retoque de foto e SlimSAM opcional local. Consulte o [guia publicado consolidado](studio-published.md). A análise e os testes abaixo descrevem o marco inicial e continuam como histórico, não como lista de pendências atuais.

## Referência e diagnóstico

Fonte oficial: https://github.com/nilbuild/page-mascot, revisão `76a44ed9180063bf4852b9dd724b656f4a828ac7`.

O componente `src/mascot.tsx` usa React >=18, duas imagens 3×3, `atan2`, zona morta de 70 px e histerese para escolher oito direções e centro. Cliques alternam expressões por temporizadores; quatro cliques próximos mostram dizzy. A deformação usa Web Animations e respeita movimento reduzido. Ponteiro fino/hover é necessário para rastrear. Não há modelo, SDK de IA, conversa, memória ou geração de desenho em runtime. Quatro expressões do atlas não são acionadas pelo fluxo atual. Node >=20 é requisito declarado de ferramentas; Vite/TypeScript/Tailwind pertencem ao desenvolvimento/site.

Criar arte nova é outro fluxo: `skills/page-mascot/scripts/generate.py` chama imagens via OpenAI ou a skill usa ferramenta de imagem do agente. O modelo padrão do snapshot é configuração, não prova de disponibilidade atual. `--skip-generate` permite processar folhas já desenhadas, mas não cria novos desenhos. Pillow, NumPy e SciPy alinham escala/ombros, removem bleed e geram WebP; o SDK OpenAI é necessário para geração via API. Verificação numérica não detecta direção semanticamente invertida; cabelo/acessórios largos e fundos quadriculados pintados são limites conhecidos.

`LICENSE` declara MIT, copyright 2026 Kamran Ahmed. Permite reutilizar código e material coberto preservando copyright e licença em cópias/porções substanciais. README oferece download das sheets; não há licença individual nem comprovação independente da procedência de cada imagem. Isso não garante direitos de terceiros sobre marcas, fotos ou semelhança. Esta implementação não copia código nem imagens da referência; usa desenho geométrico original.

## Comparação com ViraPets

ViraPets `dfd29c9` já anima sem LLM, rede, arquivos ou processo em runtime. Quatro humores respondem aos eventos do Claude e seis ou mais escalas Raster são compiladas de GIFs. A dependência de geração está na entrada da arte: `new` cria manifesto/pastas, e a pessoa precisa fornecer quatro faixas PNG. `deliver` e `build` já são determinísticos e locais, com Python/Pillow 12.3.0.

As duas folhas 3×3 de bustos do page-mascot não substituem diretamente as quatro faixas de oito poses do ViraPets; direções do mouse não equivalem a humores do Claude. Não adicionamos React nem adaptamos hooks do terminal.

## Marco histórico — primeira etapa

`site/` oferece desenho procedural no Canvas, parâmetros de aparência, prévia animada e pacote ZIP com manifesto e quatro PNGs transparentes de 2048×256. A receita JSON permite reproduzir/editar o personagem. Sem API, chave, dependências remotas ou LLM durante criação, exportação e uso. O pacote entra no `deliver`/`build` existente. Arquivos dos três pets aprovados e hooks são preservados. Arte gerada por regras simples terá acabamento diferente da arte ilustrada aprovada.

A página foi publicada e testada em https://daneiel.github.io/virapets/ (commit do site pessoal `89b2ad4`, Pages success). Foi publicada isoladamente em uma subpasta do Pages pessoal já habilitado. Fonte do plugin continua local para revisão; publicação da página não autoriza atualização da instalação nem push de mudanças do plugin. Conta GitHub verificada: daneiel. Em 19/10 o GitHub informa ViraPets público e sem Pages, apesar de notas antigas dizerem privado.

## Escolhas levantadas no marco inicial

1. **Parcialmente entregue:** 12 animais/26 combinações. Ampliar o editor por peças originais (espécies, corpo, orelhas, acessórios) preservando a receita e o pipeline — evolução natural desta etapa.
2. Importar arte própria feita em editor externo e oferecer revisão/recorte dos quatro humores — maior liberdade, exige desenho manual.
3. Adaptar direções e reações para mascotes web — formato/host adicional, separado do contrato atual de quatro humores.

No marco inicial não havia edição de foto. A versão publicada agora recorta, pixeliza, retoca e anima fotos, com segmentação local opcional. Geração de um novo personagem ilustrado por foto/texto e integração de cursor no terminal continuam fora do Studio. Aprovação artística, instalação no Claude real e importação em aparelho Android são verificações distintas.

## Validação histórica do marco inicial

6 testes Node, 14 Python, 29 Claude 2.1.303 e validate aprovados. Browser Chromium/Playwright 1.60.0 em 1440 px e 390 px: zero erros, export ZIP e receita válidos, sem overflow horizontal. Importação de texto HTML permanece literal; JSON inválido preserva a receita anterior; movimento reduzido inicia pausado. ZIPs repetidos são idênticos. Download → deliver → validate → build: 32 quadros e 87 arquivos originais preservados por SHA-256. Evidências em docs/validation/procedural-*.json, public-browser-qa.json e roundtrip.json. Não houve instalação de novo pet no Claude real nem teste de Android.
