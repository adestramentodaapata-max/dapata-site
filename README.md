# Site Dapata Pet Center (dapata.com.br)

Site estático: HTML + CSS + um JS pequeno (menu e animação), servido por nginx num container. Pesa menos de 1 MB.

## Estrutura
- `build.py`: gera todas as páginas a partir de um molde único. Textos, endereços, WhatsApp e e-mail ficam aqui.
- `site/`: o site pronto (o que vai para o servidor). `css/site.css` tem o visual, `img/marca.svg` tem o logo e o símbolo.
- `Dockerfile` + `nginx.conf`: imagem para o Coolify (links limpos, página 404, cache e gzip).

Depois de mudar texto ou configuração: `python3 build.py`.

## Antes de publicar
1. **WhatsApp e perfil do Google**: preencher `WHATSAPP` e `GOOGLE_PERFIL` no topo do `build.py`. Os selos "a confirmar" somem sozinhos.
2. **Fontes**: extrair os arquivos .woff2 de Roca e Author para `site/fonts/`, ajustar os nomes em `site/css/fontes.css` e ligar `FONTES_OFICIAIS = True`.
3. **Itens "a confirmar"** e **fotos**: ver a lista e a tabela de nomes de arquivo no `RELATORIO.md`.
4. Rodar `python3 build.py`.

## Publicar no Coolify
1. Subir esta pasta para um repositório no GitHub (privado serve).
2. No Coolify: **+ New Resource → Public/Private Repository**, escolher o repositório e a branch.
3. **Build Pack: Dockerfile**. Porta: **80**.
4. Em **Domains**, colocar `https://dapata.com.br,https://www.dapata.com.br` (o Coolify emite o SSL).
5. No registro do domínio (Registro.br ou onde estiver o DNS): registro **A** de `@` e de `www` apontando para o IP do servidor do Coolify.
6. **Deploy**. Com o webhook do GitHub ligado, cada push publica de novo.

Depois de no ar: cadastrar o site no Google Search Console e enviar `https://dapata.com.br/sitemap.xml`.

Requisito do build: Python 3 com Pillow (gera os WebP) e `rsvg-convert` (só na primeira vez, para o PNG do logo).


O portal da equipe (sistema.dapata.com.br) agora é um sistema próprio, no repositório `dapata-sistema`.
