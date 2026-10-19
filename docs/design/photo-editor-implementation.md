# Editor de foto local — primeira versão

AT-019,19/10/2026. Daniel autorizou implementar e publicar para testar. O modo procedural, prompt, temasBRABO, faviconJojo e exportadores existentes são preservados. Nenhum serviçoGradio/Prodia/freellmapi foi integrado.

## Produto e limites

Modo “Foto → pixel art local”: selecionaPNG/JPEG/WebPaté10MiB/40MP; decodifica orientação e reduz cópia a768px de lado maior. A foto fica em memória, sem nome/EXIF na receita. A máscara inicia com todos os pixels visíveis; usuário escolhe recorte assistido por pontospositivos/negativos ou pincel manter/apagar, desfaz até10máscaras. Setas/Enter permitem seleção e retoque pelo teclado. Pixelização determinística: recorta bbox da máscara, quantiza paleta2–32cores, grade16–96, contornoopcional e margens transparentes. RetoqueCanvas porcor/borracha. Usar “Aplicar” novamente substitui retoques pela nova pixelização.

Isso é recorte de foto pixelizado com movimentos simples de translação/rotação/escala. Não cria olhos/bocas novos nem redesenha expressões; quatro grupos de movimento têm oito poses distintas, mas não equivalem aos humores ilustradosJojo/Mel/Dara. Um clique pode selecionar só uma parte do animal: acrescentar pontos emoutraspartes e excluirfundo, ou corrigir manualmente. Limite128pontos. Não existe garantia de seleção perfeita de pelos, identidade ou acabamento artístico. Assets atuais intactos.

## Modelo, rede e cache

Carregador oficial `@huggingface/transformers`3.8.1,ONNXRuntimeWASMCPU emWorker módulo, singlethread, sem exigirWebGPU. SlimSAMq8 oficial `Xenova/slimsam-77-uniform`, revisão5850ab45f587c112167512ffef949107115e26a0. Pesos/configuração13.786.820bytes; runtimeJS/WASM22.528.676; soma36.315.496bytes não comprimidos. A página informa antes da ativação; pequenosarquivos da própria página não integram essa soma. Manifesto comarquivos/hashruntime emtools/site-ml/manifest.json. Runtimevendorizado, pesos remotosHF somente quando ovisitante escolhe o recurso; nodependência de instalação manual do visitante, token ouAPIdeinferência. Build/arquivosoficiais/licenças emtools/site-ml e aviso distribuído emsite/vendor/PHOTO-ML-NOTICES.txt.

Rede observada deve conter somenteGET: scripts/WASMlocais e pesos/configuraçõesHF e seusCDNs. Foto não é argumento de fetch/requisições; pixels seguempostMessage aoWorker no próprio processo dobrowser. Sem analítica ou transmissão deconteúdo. Download revelaIP/metadados derequisição ao host/CDN, não a foto. Não prometer operaçãooffline na primeira visita ou disponibilidade ilimitada dosdownloads.

Embeddings reutilizados para novos pontos da mesma imagem. CacheAPI específico`virapets-slimsam-<revision>` guarda somente arquivos remotos do modelo; sem foto/embeddings. Botão cancela/liberaWorker; outro apaga apenas essecache. Cachepodefalhar/ser removido: fluxo continua semcache e mostraerro se download falhar. Modelo indisponível mantém foto/edição e permite máscara manual ouprompt. Cancelamento não altera foto; receita e arte só saem por download deliberado. Trocar/recarregar página perde originais, salvoexportmanual da pixelart.

## Exportação e compatibilidade

Mesmosbotões exportam PNG2048×256,4faixas+pet.json+recipe.json+README noZIP,JSONreceita e quatroWebP512×512 em.wastickers. Receita guardaPNG256final derivado, não original/máscara. Aoimportar pode retocar/reanimar, mas refazerrecorte requer escolher foto de novo. Receitasproceduraisv1 continuam aceitas; campoopcionalphoto versionado/validado, tamanhoarquivo450KB,PNG256egridválidos. Nome/autoria/ID usam validação existente; draftpreservado. Export captura cópia da arte antes da montagemassíncrona para impedir mistura dequadros quando usuário edita. WebPporCanvas pode sercomperdas; importAndroidcontinua dependente deappcompatível.

Stickersaceitam rendereropcional sem alterar assinatura anterior; efeitosZzz e tempos permanecem. Código do plugin/pipeline e assets/hook não mudam. Python/Pillow é validação deintegração do projeto, não requisito do site.

## Evidências

Preencher com resultados finais no relatório docs/validation/photo-editor.json. Testes incluem core e regressão de quantização com coresminoritárias, protocoloWorker/cache/bytes, regressõesprocedurais/WebP, navegadorChromeheadless comamostrasintética, exportdecodePillow eZIP→deliver→validate. Viewports390/1440 não provam compatibilidade emtelefone físico. Firefox/Safari/aparelhos reais e importAndroid ainda não medidos. TemposCPU/RAM podem variar; tamanho de pesos não é mínimoRAM. Sem alegação de desempenho universal ou paridade artística.


## Publicação verificada

Publicado somente o site pessoal, subpasta`virapets`, commit2ff19ad93b17c43c81b2f898d680863ec2941fa4, Pagesrun39249300236 success. URL https://daneiel.github.io/virapets/ testada emChromium público: modo manual e modelo real, múltiplos pontos, cache sem nova rede, erro/retry/cancelamento, 4PNG/32quadros e4WebPanimados. Relatórios docs/validation/photo-editor.json e photo-editor-public.json. 23testesNodeaprovados; 64arquivosassets/hooks preservados. ZIP→deliver→validate aprovado emclone temporário. Sem telefonefísico/Firefox/Safari/importaçãoAndroid; sem nova sessão deplugin, cujosdados/runtimepermanecemintactos. Publicado não inclui commits deplugin.
