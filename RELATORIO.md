# Relatório final: site DaPata Pet Center (01/11/2026)

## Arquivos modificados
| Arquivo | O que mudou |
|---|---|
| `build.py` | Reescrito: dados oficiais (CNPJ, e-mail, serviços por unidade), conteúdo revisado das 7 páginas, dados estruturados, links externos em nova aba, WebP, sistema de fotos pendentes |
| `site/css/site.css` | Ajustes de rodapé, nota de agendamento, canais de contato, retrato, `picture` |
| `site/js/site.js` | Animação de entrada refeita para não deixar blocos escondidos em rolagem rápida ou salto de âncora |
| `nginx.conf` | `absolute_redirect off` (redirecionamentos corretos atrás do proxy do Coolify), www → dapata.com.br, cache também para JS |
| `site/img/*.webp` | WebP gerado de todas as fotos (−20% no total) |
| `site/img/logo-dapata.png` | Logo em PNG 1200 px para o Google (dados estruturados) |
| `site/*.html`, `sitemap.xml`, `robots.txt` | Gerados pelo build |

## Conteúdo corrigido
- Removido "o primeiro pet center de Toledo" de todas as páginas.
- História: adestramento desde 2016; pet shop e hotelaria vieram depois (ano marcado como pendente).
- Creche e hotel: castração **recomendada, não obrigatória**; exigências = V10, gripe, antirrábica, vermifugação, antiparasitário. Saíram "fêmeas fora do cio" e "foto da carteirinha" (não estão na lista confirmada).
- Socialização descrita como liberdade controlada e supervisionada, adaptação gradual; o site não diz que os cães ficam todos juntos; descanso respeitado.
- Acompanhamento humano inclusive à noite, sem detalhes de quem acompanha.
- Adestramento: escolinha **duas vezes por semana** (antes 1x/2x/3x); saiu "programa de 6 meses".
- Taxi Dog: toda Toledo, só para serviços do DaPata; saiu o limite de cães por viagem.
- Unidades com a lista oficial de serviços (incluindo venda de rações e produtos nas duas).
- Nota em todas as chamadas: pedido pelo Zoop ou mensagem não é confirmação automática; a equipe confirma.

## SEO por página
| Página | Title | Foco | Schema |
|---|---|---|---|
| `/` | Pet shop em Toledo - PR \| DaPata Pet Center | pet shop em Toledo | Organization + 2 PetStore (uma por unidade, com endereço, horário, mapa e serviços) |
| `/banho-e-tosa` | Banho e tosa em Toledo - PR, com tosa na tesoura | banho e tosa | Service + PetStore unidade 1 + Breadcrumb |
| `/creche-e-hotel` | Creche e hotel para cães em Toledo - PR | creche / hotel para cães | Service + PetStore unidade 2 + Breadcrumb |
| `/adestramento` | Adestramento de cães em Toledo - PR | adestramento | Service + PetStore unidade 2 + Breadcrumb |
| `/taxi-dog` | Taxi Dog em Toledo - PR, transporte de cães | Taxi Dog | Service (areaServed Toledo) + Breadcrumb |
| `/quem-somos` | Quem somos: a história do DaPata Pet Center | marca | Breadcrumb |
| `/unidades` | Unidades, horários e contato | endereços | Organization + 2 PetStore + Breadcrumb |

Todas: um H1, sem saltos de título, canonical, Open Graph, meta description de 140 a 155 caracteres. 404 com `noindex`. URLs limpas, `.html` e barra final redirecionam (301). Sem telefone, coordenadas ou avaliações inventadas no schema.

## Testes executados
- 31 URLs internas rastreadas no nginx: nenhuma quebrada.
- Links dos mapas idênticos aos fornecidos.
- Zoop: `target="_blank" rel="noopener noreferrer"`; clique abre nova aba e o site continua aberto (testado no navegador).
- Todos os links externos com nova aba, rel de segurança e aviso "(abre em nova aba)" para leitor de tela.
- 7 páginas em 1440, 820 e 390 px: sem rolagem lateral, sem imagem quebrada, sem erro de JavaScript.
- Menu do celular: abre, fecha com Esc e ao tocar num item; foco visível no teclado.
- JSON-LD de todas as páginas válido (JSON) e com tipos corretos.
- Varredura de termos proibidos/antigos (primeiro pet center, castrados, cio, 3x, 6 meses, Bora): nenhum.
- Não deu para testar daqui: abrir Zoop/Instagram/Google (rede bloqueada no ambiente) e o Rich Results Test do Google (fazer após publicar).

## Pendências da empresa
1. **Número do WhatsApp** → `WHATSAPP` no `build.py`. Enquanto isso, os botões levam à página de contato.
2. **Link do perfil no Google** → `GOOGLE_PERFIL`.
3. Ano da expansão para pet shop e hotelaria.
4. Tempo médio do banho e da tosa; idade mínima no adestramento.
5. Nomes e funções da equipe.
6. Fotos (abaixo). As atuais são 506x900 (compressão de WhatsApp); originais em alta melhoram muito a abertura.

## Como inserir fotos depois
Salve o arquivo em `site/img/` com o nome exato e rode `python3 build.py`. O espaço "a confirmar" é trocado pela foto automaticamente, com WebP e dimensões gerados.

| Material | Arquivo | Onde aparece |
|---|---|---|
| Fachada unidade 1 | `unidade1-fachada.jpg` | Unidades (home, banho e tosa, unidades) |
| Fachada unidade 2 | `unidade2-fachada.jpg` | Substitui a foto do pátio nas mesmas áreas |
| Equipe | `equipe.jpg` | Quem somos (home, adestramento, quem somos) |
| Carro do Taxi Dog | `taxi-dog-carro.jpg` | Topo do Taxi Dog |
| Treino | `adestramento-treino.jpg` | Topo do Adestramento |
| Creche, hotel, banho | substituir `creche.jpg`, `g1.jpg`…`g6.jpg`, `banho.jpg` mantendo o nome | Galeria e serviços |

Prefira JPG com pelo menos 1200 px no lado maior. Fotos verticais funcionam melhor nas áreas atuais.

## Ajuste 01/11, 04h20
- Site sem destaque ao nome do responsável: a história e o método falam da empresa.
- Animação de entrada removida (podia deixar fotos invisíveis em alguns visualizadores).
