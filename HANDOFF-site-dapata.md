# Handoff: site Dapata (01/11/2026)

- Projeto em /home/claude/site-dapata (build.py gera site/; Dockerfile + nginx.conf para o Coolify; README com o passo a passo).
- Prévia v2 multipágina: https://claude.ai/artifact/RuW5xTm1EeVhgcsXx1c9kx (slug c9afedad-5cc2-4018-853d-8846914bfd6d). A prévia aprovada original continua intacta (slug 90c68f0f-fe27-4cc8-bc4d-b6bfcb01b18c).
- Gerar prévia: `python3 build.py --previa /home/claude/previa` (links .html, caminhos relativos) e publicar com publish_files no mesmo slug.
- Páginas: início, banho-e-tosa, creche-e-hotel, adestramento, taxi-dog, quem-somos, unidades, 404.
- Fontes de dados usadas: memória (dapata-marca, site-institucional, escola-adestramento, taxi-dog, banho-e-tosa) e a skill responder-whatsapp-dapata (endereços, horários, rotina, requisitos, hotel).
- nginx testado localmente: / 200, /pagina 200, /pagina.html e /pagina/ → 301 para a forma limpa, 404 customizado.
- Pendente: WHATSAPP e EMAIL no build.py; fontes Roca/Author (zip ainda não chegou; depois ligar FONTES_OFICIAIS e ajustar nomes em css/fontes.css); itens "a confirmar" (tempo do banho, área do Taxi Dog, idade mínima no adestramento, ano de fundação, equipe, CNPJ); fotos de treino, banho, carro do Taxi Dog, fachada, Diamante e Belchior; repositório no GitHub + deploy no Coolify.
- Mapas (iframe do Google) não aparecem na prévia do artifact por bloqueio do sandbox; funcionam no site real.

## v3 editorial (01/11/2026, 03h20)
- Brief de reformulação aplicado sobre a v2 (mesmo artifact, versão "v3 editorial"). Paleta: oficiais (laranja só em detalhes, marrom #63230F nos blocos e botões) + neutros off-white #F7F4EE, areia #E8D9C5, grafite #292722. Terracota #B96537 do brief NÃO usada (fora da identidade oficial).
- Home: hero com foto protagonista, serviços em blocos alternados (creche e hotel separados), Nosso jeito com 6 pilares em fundo marrom, galeria assimétrica (função mosaico(), usada também em creche-e-hotel), rotina + requisitos, unidades 1 e 2, quem somos, contato "Vamos encontrar o melhor cuidado para o seu cão?" com canais.
- CTAs: marrom cheio = Zoop; contorno = falar com a equipe; link com seta = conhecer serviço.
- js/site.js: menu mobile (Esc, fecha ao clicar, trava rolagem), borda do cabeçalho ao rolar, animação de entrada respeitando redução de movimento.
- Fotos são 506x900 (compressão de WhatsApp); pedir originais em alta.

## v4 final (01/11/2026, 04h)
- Brief "Execução final" aplicado. Fatos novos: CNPJ 25.192.490/0001-04, e-mail dapatapetcenter@gmail.com, castração recomendada (não obrigatória), exigências só V10/gripe/antirrábica/vermífugo/antiparasitário, escolinha 2x/semana, Taxi Dog toda Toledo e só para serviços DaPata, história desde 2016, sem "primeiro pet center".
- build.py reescrito: FOTOS (arquivo com nome certo em site/img/ substitui o placeholder), WebP automático, links externos em nova aba, JSON-LD por unidade/serviço/breadcrumb, logo-dapata.png.
- Relatório completo em RELATORIO.md. Pendentes: WhatsApp, GOOGLE_PERFIL, ano da expansão, tempo do banho, idade mínima adestramento, equipe, fotos.
