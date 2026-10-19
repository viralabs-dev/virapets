# Recorte fluido, cabeça e seleção em modal

AT-021/AT-022,19/10/2026. Continuação autorizada do Studio publicado para testar. Nenhuma alteração em arte/modelos existentes, hooks ou instalação; nenhuma integração externa de geração.

## Animação e cabeça

Prévia usa fase temporal contínua sobre os tempos do ViraPets, com interpolação cossenoidal entre oito poses próprias por humor: balanço feliz, preparação/impulso/recuo do latido, respiração de espera e cochilo/despertar/retorno. Pausa e movimento reduzido permanecem. A foto não ganha olhos/boca novos e não há som.

Após pixelizar, a pessoa marca o centro da cabeça na **arte final256×256**, ajusta raio8–100px e ladoauto/esquerda/direita. Coordenadas/radio são normalizados na receita e transformados com a mesma escala/rotação/translação do recorte. Como a marca acontece depois da orientação/crop/resize, não usa coordenadas antigas da foto. Refazerpixelização limpa a marca; a exportação pede nova identificação. Guia circular fica emcanvas separado e nunca nos arquivos. Efeitos mudam de lado nas bordas e mantêm pixels dentro da célula.

Zzz sobem/desaparecem suavemente durante o sono e não aparecem nas fases4/5 do despertar. Traços de som pulsam no impulso do latido. PNGsfoto8quadros já incluem efeitos e manifestos usam sleepSignsnull para não duplicar. Novo lilás#cdb8f6 é visualmente adjacente ao legado#cdb7f6, evitando remoção pelo pipeline terminal que reserva a cor antiga. Procedural e pets originais não mudam. Figurinhasfoto usam32quadros porhumor (4subdivisões), tempos arredondados cumulativamente a10ms, mínimos>=8ms e limite500KB. Fotografias com alta complexidade podem exigir reduzir paleta/resolução para caber. Preview contínuo não muda o contrato8quadros dosPNG.

BotãoSimular usa a arte atual e a cabeça marcada; outro oferece exemplo sintético quando não há arte. Se há arte, preserva as edições e simula a atual. Não carrega SlimSAM. Demonstração e GIF deQA usam o mesmo renderizador; modelo/foto privada não são necessários.

## Seleção local

SlimSAM preserva múltiplos pontos positivos/negativos. ModoObjeto prefere máscara mais ampla entre candidatos com score>=0.5 e até0.15 abaixo do melhor válido; Detalhe escolhe maior score. Todo candidato precisa respeitar os pontos informados. Scores não são garantia de precisão; erro útil permite novos pontos/detalhe/pincel. Adicionar/remover áreas combina nova seleção com uma base preservada; permite partes desconectadas sem trocar o modelo por segmentador de pessoas. Não há caixa nesta versão; pontos e pincéis são controles efetivamente entregues.

Máscara interna representa pet; alternarPet/Fundo mostra o complemento e aplica pincel/refino à área escolhida, preservando a seleção lógica. Grow/shrink por disco e maioria local (raio1–4) refinam bordas. Histórico até10máscaras, desfazer/refazer, sem editar pixels dafoto original. Fundo final transparente ou preenchido comcor é calculado numa cópia ao aplicar pixelização. Trocar para transparente restaura resultado semcor; original permanece em memória intacto. Não prometer pelo perfeito nem seleção automática de qualquer objeto.

## Modal e estado

Dois lançadores abrem dialognativo; dentro dele só o painel ativo aparece/recebefoco. Foto não exibe opções procedurais nem o cachorroprocedural enquanto ainda não existe arte. Preview/exportação comuns seguem o modo ativo. Nodes movidos uma vez, sem clonarIDs: foto/máscara/receita e configurações sobrevivem à alternância e fechar/reabrir. Escape/fechar retornam foco,Tab permanece no modal, linkprompt fechaantes de abrir rota. Tema possui botão dentrodo modal; fundo opaco evita mostrar modo antigo. Layoutmobile semscrollhorizontal.

## Verificação e limites

Relatórios docs/validation/cutout-motion-selection.json e -public.json registram resultados reais. Testes unitários cobrem continuidade/limites/tempos/âncoras e máscarasdisjuntas/inversão/morfologia/escolhaObjeto. QAChromium usa exemplo sintético, modelo local real e apenasGETs de arquivos; nenhum upload. Head nos cantos, roundtripJSON, nova marca apósrecrop,32framesWebP e ausênciaZzzno despertar conferidos. Viewports390/1440 e teclado não equivalem aAndroid/iOS/Firefox/Safarireais. Sem importaçãoAndroid, som ou paridade de expressão/arte com Jojo/Mel/Dara.
