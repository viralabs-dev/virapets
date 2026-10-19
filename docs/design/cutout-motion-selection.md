# Recorte fluido, cabeça e seleção no editor inline

Estado publicado em 19/10/2026: [`d61fdfb`](https://github.com/daneiel/daneiel.github.io/commit/d61fdfbb0d89c2258b7f6989172ad04f164535a3). Consulte o [guia completo do Studio](studio-published.md) e a [arquitetura fotográfica](photo-editor-implementation.md).

## Movimento e cabeça

A prévia usa fase temporal contínua nos tempos ViraPets e interpolação cossenoidal entre oito poses de cada humor: balanço feliz, preparação/impulso/recuo do latido, respiração de espera e cochilo/despertar/retorno. Pausa e preferência de movimento reduzido são respeitadas. A transformação do recorte não desenha novas expressões e não produz áudio.

Depois de pixelizar, marque o centro da cabeça na arte final 256×256; ajuste raio de 8–100 pixels e lado automático/esquerdo/direito. Centro e raio normalizados acompanham escala/rotação/translação. Não dependem das coordenadas anteriores da foto. Refazer a pixelização limpa a marca. O guia circular é outro canvas e não entra na exportação.

Zzz sobem e desaparecem no sono, sem aparecer nos quadros 4/5 do despertar. Os raios pulsam no impulso do latido. Nas bordas, os efeitos ajustam o lado e permanecem dentro da célula. PNGs fotográficos incorporam efeitos uma vez e usam `sleepSigns` com entradas `null`; o lilás `#cdb8f6` evita o tratamento reservado do legado `#cdb7f6` no pipeline. Pets originais permanecem preservados.

A prévia é contínua; PNGs mantêm oito células por humor. Figurinhas fotográficas usam 32 quadros por humor, com tempos arredondados cumulativamente em unidades de 10 ms e limite de 500.000 bytes por WebP. Arte complexa pode exigir paleta/resolução menores. Procedural mantém oito quadros por figurinha.

A simulação usa a arte atual e sua cabeça marcada. Se não houver arte, o exemplo sintético pode ser criado localmente; isso não carrega SlimSAM. O [GIF de demonstração](https://daneiel.github.io/virapets/motion-demo.gif) é uma simulação com desenho sintético, não uma foto real de um usuário.

## Seleção e correção

SlimSAM preserva múltiplos pontos positivos e negativos. Objeto inteiro prefere uma máscara mais ampla entre candidatos com score ≥0,5 e até 0,15 abaixo do melhor válido; detalhe escolhe o maior score. Os pontos precisam ser respeitados. O score não garante precisão: corrija com novos pontos, detalhe ou pincéis. Não há seleção por caixa nesta versão.

Substituir/adicionar/remover combina a nova seleção com uma base, permitindo áreas desconectadas. A máscara interna representa o pet; Fundo exibe o complemento e aplica pincel/refino à área escolhida. Expandir/contrair usa vizinhança em disco; suavizar usa maioria local, com raio 1–4. Há histórico de até dez máscaras com desfazer/refazer.

O preenchimento por cor é calculado numa cópia ao aplicar; escolher transparente e reaplicar restaura a saída sem esse preenchimento. A foto de trabalho original não é pintada. Pelos e detalhes pequenos podem precisar de correção manual.

## Composição dos modos e regressão corrigida

A primeira versão inline ocultava só campos específicos, deixando `.studio` e `.how` fora do painel da foto. Sem arte, o canvas era limpo, mas o card Pingo e as exportações continuavam abaixo. A investigação pública confirmou `hidden=false` e `display=grid` no bloco; não havia CSS sobrescrevendo hidden ou duas instâncias. O QA anterior verificava campos e não a composição completa.

Na versão publicada, `#procedural-editor` engloba o destino procedural e instruções, ficando oculto/inert em foto. O mesmo `.studio` se move para `#photo-output`, dentro do editor fotográfico, sem clonar nós ou listeners; só aparece com arte pronta. O importador JSON compartilhado permanece acima dos painéis. Foto, máscara, cabeça, receita e configurações sobrevivem à alternância. Não há modal ou contenção de foco. Sol/lua e nome acessível identificam a troca de tema no cabeçalho.

## Evidência atual e histórica

[Relatório final público](../validation/mode-regression-public.json): desktop 1440 e viewport móvel 390, display computado, retângulos, `hidden`/`inert`, foco, ancestralidade, uma prévia/formulário, foto vazia/pronta/descartada/trocada, receitas e exportações. [Captura sem arte](../images/mode-photo-empty-1440.png) e [captura com arte](../images/mode-photo-ready-1440.png).

[Relatório anterior de movimento/seleção](../validation/cutout-public.json): cabeças nas bordas, receitas, reaplicação, Zzz ausentes ao despertar e WebPs. O modelo real foi verificado com pontos e requisições GET de arquivos, sem upload. [Relatório de espécies/tema](../validation/species-inline-public.json). Não extrapolar esses testes para aparelhos físicos, Safari/Firefox ou importação real Android.

O checkout de desenvolvimento guarda `tools/site-qa/mode-regression.cjs` para repetir o teste com Playwright e `QA_URL`. Esse arquivo e todos os testes unitários não são distribuídos automaticamente no clone público do plugin. Para servir os arquivos públicos do Studio, use o [procedimento correto](../../site/README.md#local-development-validation-and-publication).
