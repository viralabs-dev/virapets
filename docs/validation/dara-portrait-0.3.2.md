# Dara em monitor vertical — 0.3.2

O dono informou 1920×1080 e uso do monitor na vertical. Alvo considerado: 1080×1920. Mel foi aprovada e permaneceu intacta.

A redução anterior reforçava também os traços internos, fundindo detalhes dos óculos e da bandana. O perfil `detailed` conserva a média de cor interna e o contorno externo. As escalas adicionais 28, 36, 42, 44 e 46 pixels aproveitam melhor o espaço entre as seis escalas antigas. Jojo e Mel continuam com o perfil original.

A primeira tentativa com cores sem limite reproduziu quadros parcialmente atualizados no Claude. A paleta compartilhada de até 65 cores corrigiu o resultado observado: as quatro animações, incluindo os 32 quadros e a transparência, corresponderam integralmente aos dados gerados. Não foi estabelecida a causa interna do host.

Validação: 29 testes Claude, 12 Python e manifesto aprovado; Claude 2.1.301 com Flightdeck 0.4.0, configuração de usuário e instalação local, sem `--plugin-dir`. PTY de 135×110 células; a renderização de evidência usa células 8×16, resultando em 1080×1760. Isso reproduz uma janela estreita e alta, sem alegar inspeção do monitor físico. Escalas intermediárias, margem lateral, blits e ZzZ testados automaticamente. Em uma janela de 100 colunas o próprio Claude ocultou o painel lateral; essa captura não foi usada como prova visual.

Os 68 arquivos relacionados no JSON permaneceram idênticos: artes, GIFs e figurinhas dos pets e dados compilados de Jojo/Mel. A galeria também permaneceu igual. A captura animada está em `outputs/virapets/dara-monitor-vertical.gif` no workspace de entrega. O JSON contém os quadros conferidos e os hashes preservados. Na sessão já aberta do dono, aplicar com `/reload-plugins`.
