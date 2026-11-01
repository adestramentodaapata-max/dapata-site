#!/usr/bin/env python3
"""Gera as páginas do site do DaPata Pet Center a partir de um molde único.

    python3 build.py              -> gera site/*.html com links limpos (/banho-e-tosa), para o Coolify
    python3 build.py --previa DIR -> copia o site para DIR com links .html, para prévia no artifact

Textos: funções p_* no fim do arquivo. Dados da empresa: bloco de configuração abaixo.
Fotos novas: ver FOTOS e o RELATORIO.md (basta salvar o arquivo com o nome indicado em site/img/ e rodar de novo).
"""
import html as _html, json, re, shutil, subprocess, sys
from pathlib import Path
from urllib.parse import quote_plus

# ---------------------------------------------------------------- configuração
BASE_URL = "https://dapata.com.br"
NOME = "DaPata Pet Center"
WHATSAPP = "5545998499037"  # canal geral das duas unidades
EMAIL = "dapatapetcenter@gmail.com"
CNPJ = "25.192.490/0001-04"
GOOGLE_PERFIL = None     # [INSERIR LINK DO PERFIL DA EMPRESA NO GOOGLE]
FONTES_OFICIAIS = False  # True quando Roca e Author estiverem em site/fonts/ (ver css/fontes.css)
ZOOP = "https://linktr.ee/zoop.pet"
INSTAGRAM = "https://www.instagram.com/dapata.petcenter/"

UNIDADES = {
    "banho": {"id": "unidade-banho-e-tosa", "num": 1, "nome": "Banho e tosa",
              "rua": "Av. Nossa Senhora de Fátima, 202",
              "horario": "Seg a sex, 8h às 18h · Sáb, 8h às 12h",
              "horas": [(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "08:00", "18:00"), (["Saturday"], "08:00", "12:00")],
              "servicos": ["Banho", "Tosa na máquina", "Tosa na tesoura", "Venda de rações", "Venda de produtos para pets"]},
    "creche": {"id": "unidade-creche-hotel-adestramento", "num": 2, "nome": "Creche, hotel e adestramento",
               "rua": "Av. Senador Atílio Fontana, 5085",
               "horario": "Seg a sex, 8h às 18h30 · Sáb, 8h às 12h",
               "horas": [(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "08:00", "18:30"), (["Saturday"], "08:00", "12:00")],
               "servicos": ["Creche canina", "Hotel para cães", "Adestramento", "Venda de rações", "Venda de produtos para pets"]},
}

# Fotos que ainda faltam: salve o arquivo com este nome em site/img/ e rode o build.
# Enquanto o arquivo não existir, o site mostra um espaço reservado com o aviso "a confirmar".
FOTOS = {
    "unidade1": ("unidade1-fachada.jpg", "Fachada da unidade de banho e tosa do DaPata"),
    "unidade2": ("unidade2-fachada.jpg", "Fachada da unidade de creche, hotel e adestramento do DaPata"),
    "responsavel": ("responsavel-luiz-felipe.jpg", "Luiz Felipe Turmina, responsável pelo DaPata"),
    "equipe": ("equipe.jpg", "Equipe do DaPata Pet Center"),
    "taxi": ("taxi-dog-carro.jpg", "Carro do Taxi Dog do DaPata"),
    "treino": ("adestramento-treino.jpg", "Treino de adestramento no DaPata"),
}

ROOT = Path(__file__).parent
SITE = ROOT / "site"
IMG = SITE / "img"
PREVIA = False


# ---------------------------------------------------------------- utilidades
def link(slug):
    if slug in ("", "index"):
        return "index.html" if PREVIA else "/"
    base, _, ancora = slug.partition("#")
    url = f"{base}.html" if PREVIA else f"/{base}"
    return url + (f"#{ancora}" if ancora else "")


MOSTRAR_PENDENCIAS = False  # True para ver os itens "a confirmar" ao revisar


def pend(txt=""):
    if not MOSTRAR_PENDENCIAS:
        return ""
    return f'<span class="pend">{(txt + " a confirmar") if txt else "a confirmar"}</span>'


def maps(rua):
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(f"{rua}, Toledo PR")


def maps_embed(rua):
    return "https://maps.google.com/maps?output=embed&z=16&q=" + quote_plus(f"{rua}, Toledo - PR")


def zap_href():
    return f"https://wa.me/{WHATSAPP}" if WHATSAPP else link("unidades#contato")


_TAM = {}


def tamanho(arq):
    if arq not in _TAM:
        try:
            from PIL import Image
            with Image.open(IMG / arq) as im:
                _TAM[arq] = im.size
        except Exception:
            _TAM[arq] = (506, 900)
    return _TAM[arq]


def img(arq, alt, cls="", lazy=True, pos=None, prioridade=False, estilo=""):
    """<picture> com WebP (gerado no build) e JPG de reserva; largura e altura reais evitam salto de layout."""
    w, h = tamanho(arq)
    st = ";".join(x for x in (f"object-position:{pos}" if pos else "", estilo) if x)
    attrs = (f' class="{cls}"' if cls else "") + (f' style="{st}"' if st else "")
    carga = ' fetchpriority="high"' if prioridade else (' loading="lazy" decoding="async"' if lazy else "")
    webp = Path(arq).with_suffix(".webp").name
    return (f'<picture><source srcset="img/{webp}" type="image/webp">'
            f'<img src="img/{arq}" alt="{alt}" width="{w}" height="{h}"{attrs}{carga}></picture>')


def tem_foto(chave):
    return (IMG / FOTOS[chave][0]).exists()


# ---------------------------------------------------------------- ícones
ICO = {
    "externo": '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    "cadeado": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "calendario": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "estrela": '<circle cx="12" cy="9" r="6"/><path d="M9 14.5L7.5 22l4.5-2.5 4.5 2.5-1.5-7.5"/>',
    "pata": '<circle cx="7" cy="9" r="2"/><circle cx="12" cy="6" r="2"/><circle cx="17" cy="9" r="2"/><path d="M12 12c-3 0-6 3-6 6 0 2 2 3 6 3s6-1 6-3c0-3-3-6-6-6z"/>',
    "sacola": '<path d="M5 8h14l-1 13H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "seta": '<circle cx="12" cy="12" r="10"/><path d="M8 12h8M13 8l4 4-4 4"/>',
    "banho": '<path d="M4 12h16v3a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M6 12V6a2 2 0 0 1 4 0"/><path d="M8 20l-1 2M16 20l1 2"/>',
    "casa": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>',
    "medalha": '<circle cx="12" cy="8" r="5"/><path d="M9 12l-2 9 5-3 5 3-2-9"/>',
    "carro": '<path d="M5 17h14v-4l-2-5H7l-2 5z"/><circle cx="8" cy="17" r="2"/><circle cx="16" cy="17" r="2"/><path d="M5 13h14"/>',
    "tesoura": '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4L8.1 15.9M14.5 14.5L20 20M8.1 8.1L12 12"/>',
    "laco": '<path d="M12 12L4 7v10zM12 12l8-5v10z"/><circle cx="12" cy="12" r="2"/>',
    "lua": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    "sol": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "escudo": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "camera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    "casa2": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><circle cx="12" cy="15" r="2"/>',
    "doc": '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 13h7M9 17h5"/>',
    "grupo": '<circle cx="8" cy="9" r="3"/><circle cx="16" cy="9" r="3"/><path d="M2 20c0-3 3-5 6-5s6 2 6 5M12 20c0-3 3-5 6-5 1.5 0 3 .5 4 1.3"/>',
    "neve": '<path d="M12 2v20M4 6l16 12M20 6L4 18"/>',
    "rota": '<circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M8 19h7a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h7"/>',
    "caixa": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M3 11h18M8 7V4h8v3"/>',
    "zap": '<path d="M3 21l1.6-4.7A8.5 8.5 0 1 1 8 19.6z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 .8a4 4 0 0 1-1.8-1.8l.8-1-1-2z"/>',
    "insta": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8" fill="currentColor"/>',
    "agenda": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4M8 15h3"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "pin": '<path d="M12 21s7-6 7-12a7 7 0 0 0-14 0c0 6 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "folha": '<path d="M5 19c0-8 6-14 15-14 0 9-6 15-14 15"/><path d="M5 19l7-7"/>',
    "coracao": '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
}


def svg_ico(nome):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICO[nome]}</svg>')


def ico(nome):
    return f'<div class="ico">{svg_ico(nome)}</div>'


def simbolo(cls="sim"):
    return (f'<svg class="{cls}" viewBox="0 0 389.94 347.77" role="img" aria-label="Símbolo DaPata">'
            f'<use href="img/marca.svg#simbolo"/></svg>')


def foto_pend(chave, rotulo):
    """Espaço reservado para foto que ainda não existe. O nome do arquivo esperado fica no HTML."""
    arq = FOTOS[chave][0] if chave in FOTOS else ""
    return (f'<div class="foto-pend" data-arquivo="img/{arq}"><div>'
            f'<svg viewBox="0 0 389.94 347.77" aria-hidden="true"><use href="img/marca.svg#simbolo"/></svg>'
            f'{("<p>" + pend(rotulo) + "</p>") if MOSTRAR_PENDENCIAS else ""}</div></div>')


def foto(chave, rotulo, cls="foto", pos=None, lazy=True):
    if tem_foto(chave):
        arq, alt = FOTOS[chave]
        return img(arq, alt, cls, lazy=lazy, pos=pos)
    return foto_pend(chave, rotulo)


# ---------------------------------------------------------------- dados estruturados
def _horas(u):
    return [{"@type": "OpeningHoursSpecification", "dayOfWeek": d, "opens": a, "closes": f} for d, a, f in u["horas"]]


def org():
    o = {"@type": "Organization", "@id": f"{BASE_URL}/#organizacao", "name": NOME, "url": BASE_URL + "/",
         "logo": f"{BASE_URL}/img/logo-dapata.png", "email": EMAIL, "taxID": CNPJ,
         "sameAs": [INSTAGRAM] + ([GOOGLE_PERFIL] if GOOGLE_PERFIL else [])}
    if WHATSAPP:
        o["telephone"] = "+" + WHATSAPP
    return o


def unidade_ld(k):
    u = UNIDADES[k]
    d = {"@type": "PetStore", "@id": f"{BASE_URL}/unidades#{u['id']}",
         "name": f"{NOME} · Unidade {u['num']} · {u['nome']}",
         "url": f"{BASE_URL}/unidades", "image": f"{BASE_URL}/img/hero.jpg",
         "email": EMAIL, "parentOrganization": {"@id": f"{BASE_URL}/#organizacao"},
         "address": {"@type": "PostalAddress", "streetAddress": u["rua"], "addressLocality": "Toledo",
                     "addressRegion": "PR", "addressCountry": "BR"},
         "hasMap": maps(u["rua"]), "openingHoursSpecification": _horas(u),
         "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s}} for s in u["servicos"]]}
    if WHATSAPP:
        d["telephone"] = "+" + WHATSAPP
    return d


SERVICOS_LD = {
    "banho-e-tosa": ("Banho e tosa", "banho", "Banho, tosa na máquina e tosa na tesoura com manejo respeitoso e atenção ao comportamento de cada cão."),
    "creche-e-hotel": ("Creche e hotel para cães", "creche", "Creche canina e hospedagem com adaptação gradual, interações supervisionadas e acompanhamento humano inclusive à noite."),
    "adestramento": ("Adestramento de cães", "creche", "Escolinha de adestramento, atendimento na residência e consultoria comportamental com protocolo escrito."),
    "taxi-dog": ("Taxi Dog", "creche", "Transporte de cães em Toledo para os serviços do DaPata, em veículo com ar-condicionado e caixas de transporte."),
}


def jsonld(slug, titulo):
    g = []
    if slug in ("index", "unidades"):
        g += [org(), unidade_ld("banho"), unidade_ld("creche")]
    if slug in SERVICOS_LD:
        nome, uk, desc = SERVICOS_LD[slug]
        g.append({"@type": "Service", "name": nome, "description": desc, "serviceType": nome,
                  "provider": {"@id": f"{BASE_URL}/unidades#{UNIDADES[uk]['id']}"},
                  "areaServed": {"@type": "City", "name": "Toledo, PR"}, "url": f"{BASE_URL}/{slug}"})
    if slug not in ("index", "404"):
        g.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": titulo, "item": f"{BASE_URL}/{slug}"}]})
    if not g:
        return ""
    if slug in SERVICOS_LD and slug not in ("index", "unidades"):
        g.append(unidade_ld(SERVICOS_LD[slug][1]))
    return ('<script type="application/ld+json">' +
            json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False) + "</script>")


# ---------------------------------------------------------------- molde
NAV = [("banho-e-tosa", "Banho e tosa"), ("creche-e-hotel", "Creche e hotel"),
       ("adestramento", "Adestramento"), ("taxi-dog", "Taxi Dog"),
       ("quem-somos", "Quem somos"), ("unidades", "Unidades"), ("unidades#contato", "Contato")]
SISTEMA = "https://sistema.dapata.com.br"

ZAP_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.4-.2z"/></svg>'


def pagina(slug, titulo, titulo_seo, descricao, corpo, imagem="hero.jpg", preload=None):
    canon = BASE_URL + ("/" if slug == "index" else f"/{slug}")
    fontes = ('<link rel="stylesheet" href="css/fontes.css">' if FONTES_OFICIAIS else
              '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
              '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700;9..144,900&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">')
    atual = ' aria-current="page"'
    nav = "".join(f'<li><a href="{link(s)}"{atual if s == slug else ""}>{t}</a></li>' for s, t in NAV)
    servicos_menu = "".join(f'<li><a href="{link(s)}"{atual if s == slug else ""}>{t}</a></li>' for s, t in NAV[:4])
    zap_txt = "WhatsApp"
    robots = '<meta name="robots" content="noindex">' if slug == "404" else ""
    pre = (f'<link rel="preload" as="image" href="img/{Path(preload).with_suffix(".webp").name}" type="image/webp" fetchpriority="high">'
           if preload else "")
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo_seo}</title>
<meta name="description" content="{descricao}">
{robots}<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="{NOME}">
<meta property="og:title" content="{titulo_seo}"><meta property="og:description" content="{descricao}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{BASE_URL}/img/{imagem}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#63230F">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
{pre}
{fontes}
<link rel="stylesheet" href="css/site.css">
<script>document.documentElement.classList.add("js")</script>
<script src="js/site.js" defer></script>
{jsonld(slug, titulo)}
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header>
  <div class="wrap topo">
    <a class="marca" href="{link('index')}" aria-label="{NOME}, página inicial"><svg viewBox="0 0 837.21 214.66" aria-hidden="true"><use href="img/marca.svg#logo"/></svg></a>
    <nav class="principal" aria-label="Principal"><ul>
      <li><a href="{link('index')}"{atual if slug == 'index' else ""}>Início</a></li>
      <li class="sub"><button type="button" aria-expanded="false" aria-controls="sub-servicos"{' data-atual' if slug in ('banho-e-tosa','creche-e-hotel','adestramento','taxi-dog') else ''}>Serviços<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2"/></svg></button>
        <ul id="sub-servicos">{servicos_menu}</ul></li>
      <li><a href="{link('unidades')}"{atual if slug == 'unidades' else ""}>Unidades</a></li>
      <li><a href="{link('quem-somos')}"{atual if slug == 'quem-somos' else ""}>Quem somos</a></li>
      <li><a href="{link('unidades#contato')}">Contato</a></li>
    </ul></nav>
    <div class="topo-acoes">
      <a class="btn btn-contorno" href="{ZOOP}">{svg_ico("externo")}Solicitar na Zoop</a>
      <a class="btn btn-pri" href="{zap_href()}">{svg_ico("zap")}Fale com a equipe</a>
      <a class="equipe-ico" href="{SISTEMA}" aria-label="Área da equipe" title="Área da equipe">{svg_ico("cadeado")}</a>
    </div>
    <details class="menu"><summary aria-label="Abrir menu"><span class="barras" aria-hidden="true"></span>Menu</summary><nav class="gaveta" aria-label="Menu do celular"><ul>{nav}</ul><div class="acoes"><a class="btn btn-pri" href="{zap_href()}">{svg_ico("zap")}Fale com a equipe</a><a class="btn btn-contorno" href="{ZOOP}">{svg_ico("externo")}Solicitar na Zoop</a></div><a class="gaveta-equipe" href="{SISTEMA}">{svg_ico("cadeado")}Área da equipe</a></nav></details>
  </div>
</header>
<main id="conteudo">
{corpo}
</main>
<footer>
  <div class="wrap">
    <div class="colunas">
      <div>
        <a class="marca" href="{link('index')}" aria-label="{NOME}, página inicial"><svg viewBox="0 0 837.21 214.66" aria-hidden="true"><use href="img/marca.svg#logo"/></svg></a>
        <p class="assina">Da pata ao coração, um gesto de conexão!</p>
      </div>
      <div><h2 class="rod">Serviços</h2><ul>
        <li><a href="{link('banho-e-tosa')}">Banho e tosa</a></li><li><a href="{link('creche-e-hotel')}">Creche e hotel</a></li>
        <li><a href="{link('adestramento')}">Adestramento</a></li><li><a href="{link('taxi-dog')}">Taxi Dog</a></li></ul></div>
      <div><h2 class="rod">DaPata</h2><ul>
        <li><a href="{link('quem-somos')}">Quem somos</a></li><li><a href="{link('unidades')}">Unidades e horários</a></li>
        <li><a href="{ZOOP}">Solicitar na Zoop</a></li></ul></div>
      <div><h2 class="rod">Contato</h2><ul>
        <li><a href="{zap_href()}">{zap_txt}</a></li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li><a href="{INSTAGRAM}">Instagram @dapata.petcenter</a></li>
        <li><a class="equipe-rod" href="{SISTEMA}">{svg_ico("cadeado")}Área da equipe</a></li></ul></div>
    </div>
    <p class="base"><span>{NOME} · Toledo - PR · CNPJ {CNPJ}</span><span>© 2026</span></p>
  </div>
</footer>
<a class="zap" href="{zap_href()}" aria-label="Falar com a equipe pelo WhatsApp">{ZAP_SVG}</a>
</body>
</html>
'''


NOTA_AGENDA = ('<p class="nota">O pedido feito pelo Zoop ou por mensagem não é uma confirmação automática. '
               'A equipe do DaPata confirma data, horário e disponibilidade com você.</p>')


def mosaico():
    return f'''<div class="mosaico">
      <figure class="m1 surge">{img("g1.jpg", "Dois buldogues franceses no pátio da creche, com a placa do DaPata ao fundo", pos="center 60%")}<figcaption>Creche DaPata</figcaption></figure>
      <figure class="m2 surge">{img("g4.jpg", "Husky de boca aberta no pátio da creche", pos="center 30%")}</figure>
      <figure class="m3 surge">{img("g3.jpg", "Cão de pelo dourado usando óculos escuros, deitado na creche", pos="center 25%")}</figure>
      <figure class="m4 surge">{img("g6.jpg", "Cães no espaço interno do hotel", pos="center 62%")}<figcaption>Espaço interno</figcaption></figure>
      <figure class="m5 surge">{img("g2.jpg", "Shih-tzu deitado no pátio, com outro cão ao fundo", pos="center 55%")}</figure>
      <figure class="m6 surge">{img("g5.jpg", "Dois cães idosos lado a lado no pátio da creche", pos="center 40%")}</figure>
    </div>'''


def canais():
    zap = (f'<a class="canal" href="{zap_href()}"><span class="ic">{svg_ico("zap")}</span><span><b>WhatsApp</b><span>Canal geral das duas unidades</span></span></a>'
           if WHATSAPP else
           f'<div class="canal"><span class="ic">{svg_ico("zap")}</span><span><b>WhatsApp</b><span>Canal geral das duas unidades · {pend("número")}</span></span></div>')
    return f'''<div class="canais">
  <a class="canal" href="{ZOOP}"><span class="ic">{svg_ico("agenda")}</span><span><b>Agendamento pelo Zoop</b><span>Banho, creche, hotel e adestramento</span></span></a>
  {zap}
  <a class="canal" href="mailto:{EMAIL}"><span class="ic">{svg_ico("mail")}</span><span><b>E-mail</b><span>{EMAIL}</span></span></a>
  <a class="canal" href="{INSTAGRAM}"><span class="ic">{svg_ico("insta")}</span><span><b>Instagram</b><span>@dapata.petcenter</span></span></a>
</div>'''


def chamada(titulo="Vamos encontrar o melhor cuidado para o seu cão?",
            texto="Conte para a gente o que ele precisa. A equipe orienta, e o agendamento é feito pelo Zoop.",
            com_canais=False):
    return f'''<section class="chamada areia" id="contato" aria-labelledby="contato-titulo">
  <div class="wrap">
    <p class="kicker">Contato</p>
    <h2 id="contato-titulo">{titulo}</h2>
    <p>{texto}</p>
    {caminhos()}
    {canais() if com_canais else ""}
    {NOTA_AGENDA}
  </div>
</section>'''


def cartao_unidade(k, capa, completo=False, mapa=False):
    u = UNIDADES[k]
    servs = "".join(f"<li>{s}</li>" for s in u["servicos"])
    m = (f'<iframe class="mapa" title="Mapa da unidade {u["num"]}: {u["rua"]}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
         f'src="{maps_embed(u["rua"])}"></iframe>') if mapa else ""
    extra = ""
    if completo and k == "creche":
        extra = "<dt>Hotel</dt><dd>Entrada e saída de seg a sex, 8h às 12h e 13h30 às 18h30 · Sáb, 8h às 12h</dd>"
    return f'''<article class="unidade surge" id="{u["id"]}">
  <div class="capa">{capa}<span class="tag">Unidade {u["num"]}</span></div>
  <div class="corpo">
    <h3>{u["nome"]}</h3>
    <dl><dt>Endereço</dt><dd>{u["rua"]}, Toledo - PR</dd><dt>Horário</dt><dd>{u["horario"]}</dd>{extra}</dl>
    <ul class="lista servs">{servs}</ul>
    {m}
    <a class="mais" href="{maps(u["rua"])}">Ver no Google Maps</a>
  </div>
</article>'''


def capa_unidade(k):
    chave = "unidade1" if k == "banho" else "unidade2"
    if tem_foto(chave):
        return img(FOTOS[chave][0], FOTOS[chave][1])
    if k == "creche":  # foto real do pátio da unidade 2, com a placa do DaPata
        return img("g1.jpg", "Pátio da unidade de creche e hotel, com a placa do DaPata", pos="center 18%")
    return (f'<div class="vazia" data-arquivo="img/{FOTOS[chave][0]}"><div><svg viewBox="0 0 389.94 347.77" aria-hidden="true">'
            f'<use href="img/marca.svg#simbolo"/></svg></div></div>')


def perguntas(itens):
    return '<div class="perguntas">' + "".join(
        f'<details><summary>{p}</summary><p>{r}</p></details>' for p, r in itens if r.strip()) + "</div>"


def topo(kicker, h1, lead, arte, botoes=None):
    botoes = botoes or f'<a class="btn btn-pri" href="{zap_href()}">{svg_ico("zap")}Fale com a equipe</a><a class="btn btn-contorno" href="{ZOOP}">{svg_ico("externo")}Solicitar na Zoop</a>'
    return f'''<section class="pagina-topo">
  <div class="wrap">
    <div><p class="kicker">{kicker}</p><h1>{h1}</h1><p class="lead">{lead}</p><div class="acoes">{botoes}</div></div>
    {arte}
  </div>
</section>'''


REQUISITOS = '''<ul>
          <li>Vacina V10 em dia.</li>
          <li>Vacina contra gripe em dia.</li>
          <li>Vacina antirrábica em dia.</li>
          <li>Vermifugação em dia.</li>
          <li>Antiparasitário em dia.</li>
        </ul>'''

BOM_SABER = '''<ul class="lista">
        <li><b>Castração:</b> recomendada para machos, mas não obrigatória. Dependendo do comportamento e da convivência, o macho não castrado pode precisar ficar separado dos demais.</li>
        <li><b>Adaptação:</b> é gradual, com avaliação do cão e controle das interações desde o primeiro dia.</li>
        <li><b>Socialização:</b> cães com dificuldade de convívio participam com liberdade controlada e supervisionada, preservando a segurança dele e dos outros cães.</li>
      </ul>'''


# ---------------------------------------------------------------- páginas
def card_servico(midia, icone, titulo, texto, href):
    return f'''<article class="srv">
  <a class="srv-link" href="{href}">
    <div class="srv-midia">{midia}</div>
    <span class="srv-ico">{svg_ico(icone)}</span>
    <div class="srv-corpo"><h3>{titulo}</h3><p>{texto}</p><span class="srv-mais">{svg_ico("seta")}Saiba mais</span></div>
  </a>
</article>'''


def tile(icone, cor):
    return f'<div class="srv-tile srv-tile-{cor}" aria-hidden="true">{svg_ico(icone)}</div>'


def caminhos():
    zap_card = (f'''<a class="caminho caminho-zap" href="{zap_href()}">
      <span class="caminho-ico">{svg_ico("zap")}</span>
      <span class="caminho-tit">Fale com a equipe</span>
      <span class="caminho-txt">Tire dúvidas, conte sobre o seu cão e receba orientação. WhatsApp geral das duas unidades.</span>
      <span class="caminho-cta">Abrir WhatsApp</span></a>''')
    return f'''<div class="caminhos">
    {zap_card}
    <a class="caminho caminho-zoop" href="{ZOOP}">
      <span class="caminho-ico">{svg_ico("calendario")}</span>
      <span class="caminho-tit">Solicite pela Zoop</span>
      <span class="caminho-txt">Peça banho, creche, hotel ou adestramento pela plataforma. A equipe confirma data e horário com você.</span>
      <span class="caminho-cta">Abrir a Zoop</span></a>
  </div>'''


def p_index():
    taxi_midia = img(FOTOS["taxi"][0], FOTOS["taxi"][1]) if tem_foto("taxi") else tile("carro", "marrom")
    corpo = f'''<section class="hero5" aria-labelledby="h1">
  <div class="hero5-foto">{img("hero.jpg", "Golden retriever sorrindo no pátio da creche do DaPata", lazy=False, prioridade=True, pos="center 28%")}</div>
  <div class="wrap hero5-wrap">
    <div class="hero5-texto">
      <p class="kicker">Pet center em Toledo - PR</p>
      <h1 id="h1">Seu bem mais precioso em mãos que <em>entendem de cachorro.</em></h1>
      <p class="lead">Cuidado, estrutura e conhecimento para o bem-estar do seu cão, com atendimento personalizado e foco em comportamento.</p>
      <div class="acoes"><a class="btn btn-pri btn-g" href="{zap_href()}">{svg_ico("zap")}Fale com a equipe</a><a class="btn btn-sec btn-g" href="#servicos">Conheça nossos serviços</a></div>
      <ul class="selos">
        <li>{svg_ico("calendario")}<span>Experiência<br>desde 2016</span></li>
        <li>{svg_ico("estrela")}<span>10 anos em<br>adestramento</span></li>
        <li>{svg_ico("pata")}<span>Estrutura<br>completa</span></li>
        <li>{svg_ico("coracao")}<span>Atendimento<br>personalizado</span></li>
      </ul>
    </div>
  </div>
</section>

<section id="servicos" class="servicos5" aria-labelledby="servicos-titulo">
  <div class="wrap">
    <div class="cabeca dupla">
      <div><p class="kicker">Nossos serviços</p><h2 id="servicos-titulo">Tudo o que o seu cão precisa, em um só lugar.</h2></div>
      <p>Serviços integrados, com uma equipe que entende de comportamento e uma rotina pensada para o equilíbrio e o bem-estar do seu cão.</p>
    </div>
    <div class="srv-grade">
      {card_servico(img("banho.jpg", "Poodle branca recém-tosada, com laço rosa", pos="center 40%"), "tesoura", "Banho e Tosa", "Higiene, bem-estar e cuidado com respeito às características de cada cão.", link("banho-e-tosa"))}
      {card_servico(img("creche.jpg", "Dois goldens no pátio ensolarado da creche", pos="center 30%"), "pata", "Creche e Hotel", "Socialização, rotina, atividades e hospedagem com segurança.", link("creche-e-hotel"))}
      {card_servico(img("adest.jpg", "Cão sentado olhando atento para o treinador", pos="center 30%"), "estrela", "Adestramento", "Educação, foco e vínculo para uma convivência mais leve e equilibrada.", link("adestramento"))}
      {card_servico(taxi_midia, "carro", "TáxiDog", "Transporte seguro e confortável para os serviços da DaPata, em toda Toledo.", link("taxi-dog"))}
      {card_servico(tile("sacola", "laranja"), "sacola", "Produtos Pet", "Rações e produtos selecionados para o dia a dia do seu cão, nas duas unidades.", link("unidades"))}
    </div>
  </div>
</section>

<section class="jeito5" aria-labelledby="jeito-titulo">
  <div class="wrap jeito5-grade">
    <div class="jeito5-fotos">
      <figure class="j-a">{img("g5.jpg", "Dois cães sorrindo lado a lado no pátio da creche", pos="center 45%")}</figure>
      <figure class="j-b">{img("g6.jpg", "Cães no espaço interno do hotel", pos="center 62%")}</figure>
      <div class="j-num"><b>2016</b><span>o começo, no adestramento</span></div>
    </div>
    <div>
      <p class="kicker">O jeito DaPata de cuidar</p>
      <h2 id="jeito-titulo">Cada cão tem um jeito. O cuidado parte dele.</h2>
      <p class="jeito5-intro">Antes de qualquer serviço vem a leitura do cão: como ele chega, do que tem medo, o que deixa ele tranquilo. É isso que orienta o banho, a rotina da creche e o treino.</p>
      <ol class="jeito5-lista">
        <li><h3>Atendimento personalizado</h3><p>As características e necessidades de cada cão e de cada tutor definem o atendimento.</p></li>
        <li><h3>Conhecimento em comportamento</h3><p>A base do trabalho vem de anos de adestramento e leitura canina.</p></li>
        <li><h3>Manejo respeitoso</h3><p>No ritmo de cada cão, inclusive dos que têm medo ou dificuldade.</p></li>
        <li><h3>Adaptação individualizada</h3><p>Gradual, com avaliação e controle das interações.</p></li>
        <li><h3>Enriquecimento ambiental</h3><p>Piscina, chafariz, frutas congeladas e atividades sensoriais.</p></li>
        <li><h3>Estrutura preparada</h3><p>Áreas internas e externas e espaços de descanso organizados por perfil.</p></li>
        <li><h3>Segurança e acompanhamento</h3><p>Interações supervisionadas e acompanhamento humano, inclusive à noite.</p></li>
      </ol>
    </div>
  </div>
</section>

<section class="historia5" aria-labelledby="hist-titulo">
  <div class="wrap historia5-grade">
    <div class="historia5-texto">
      <p class="kicker">Nossa história</p>
      <h2 id="hist-titulo">Mais do que cuidar. <em>Entender cada cão.</em></h2>
      <p>O DaPata nasceu do amor pelos animais e da vontade de fazer diferente. A história começou em 2016, com o adestramento, e com ela veio a base que guia tudo até hoje: vínculo, conhecimento e atendimento personalizado.</p>
      <p>Com o tempo, o trabalho cresceu para banho e tosa, creche, hotel e produtos pet. Hoje são duas unidades em Toledo, com a mesma forma de olhar para cada cão.</p>
      <ol class="linha">
        <li><b>2016</b><span>Começo com o adestramento</span></li>
        <li><b>Depois</b><span>Banho e tosa, creche, hotel e produtos</span></li>
        <li><b>Hoje</b><span>Duas unidades em Toledo</span></li>
      </ol>
      <a class="mais" href="{link('quem-somos')}">Conhecer a nossa história</a>
    </div>
    <figure class="historia5-foto">{img(FOTOS["equipe"][0], FOTOS["equipe"][1]) if tem_foto("equipe") else img("g1.jpg", "Pátio da creche do DaPata, com a placa da empresa ao fundo", pos="center 40%")}</figure>
  </div>
</section>

<section class="estrutura5" aria-labelledby="estr-titulo">
  <div class="wrap">
    <div class="cabeca dupla">
      <div><p class="kicker">Estrutura e rotina</p><h2 id="estr-titulo">Um dia pensado para o corpo e para a cabeça</h2></div>
      <p>Momentos reais da creche e do hotel, registrados pela equipe e enviados aos tutores no grupo de WhatsApp.</p>
    </div>
    {mosaico()}
    <ul class="recursos">
      <li>{svg_ico("neve")}Piscina e chafariz</li>
      <li>{svg_ico("folha")}Atividades sensoriais</li>
      <li>{svg_ico("pata")}Enriquecimento ambiental</li>
      <li>{svg_ico("lua")}Espaços de descanso</li>
      <li>{svg_ico("grupo")}Interações supervisionadas</li>
      <li>{svg_ico("escudo")}Acompanhamento inclusive à noite</li>
    </ul>
  </div>
</section>

<section class="areia" id="creche" aria-labelledby="rotina-titulo">
  <div class="wrap">
    <div class="cabeca dupla">
      <div><p class="kicker">Creche e hotel</p><h2 id="rotina-titulo">Como é o dia do seu cão com a gente</h2></div>
      <p>Uma rotina com atividade e descanso, organizada conforme o perfil e a segurança de cada cão.</p>
    </div>
    <div class="rotina">
      <ol class="linha-tempo">
        <li><b>Manhã</b><span>Atividades externas, sol e descanso.</span></li>
        <li><b>Tarde</b><span>Relaxamento no espaço interno e brincadeiras na área externa.</span></li>
        <li><b>Noite</b><span>No hotel, descanso respeitado, em espaço organizado conforme o perfil e a necessidade de tranquilidade de cada cão.</span></li>
        <li><b>Sempre</b><span>Acompanhamento humano, inclusive à noite. Fotos e vídeos no grupo de WhatsApp dos tutores.</span></li>
      </ol>
      <div class="checklist">
        <h3>Para participar</h3>
        {REQUISITOS}
        <p class="obs">Castração de machos é recomendada, não obrigatória. A adaptação é gradual e acompanhada.</p>
        <p><a class="mais" href="{link('creche-e-hotel#participar')}">Regras e adaptação</a></p>
      </div>
    </div>
  </div>
</section>

<section id="unidades" aria-labelledby="unidades-titulo">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Unidades</p><h2 id="unidades-titulo">Duas unidades em Toledo</h2></div>
    <div class="unidades">{cartao_unidade("banho", capa_unidade("banho"))}{cartao_unidade("creche", capa_unidade("creche"))}</div>
  </div>
</section>

<section class="contato5" id="contato" aria-labelledby="contato-titulo">
  <div class="wrap">
    <div class="contato5-cab">
      <p class="kicker">Contato</p>
      <h2 id="contato-titulo">Vamos encontrar o melhor cuidado para o seu cão?</h2>
      <p>Dois caminhos, cada um para uma coisa: conversar com a equipe ou solicitar o serviço.</p>
    </div>
    {caminhos()}
    {NOTA_AGENDA}
  </div>
</section>'''
    return pagina("index", "Início", "Pet shop em Toledo - PR | DaPata Pet Center",
                  "DaPata Pet Center em Toledo - PR: banho e tosa, creche e hotel para cães, adestramento desde 2016, TáxiDog e produtos pet. Duas unidades e atendimento personalizado.",
                  corpo, preload="hero.jpg")


def p_banho():
    corpo = f'''{topo("Banho e tosa · Unidade 1", "Banho e tosa em Toledo, no ritmo do seu cão.",
        "Cheiroso e bonito, sim. Mas antes da água e da tesoura vem o cuidado: manejo respeitoso e atenção ao comportamento de cada cão, inclusive dos que sentem medo.",
        img("banho.jpg", "Poodle branca recém-tosada, com laço rosa", "foto", lazy=False, prioridade=True, pos="center 40%"))}

<section aria-labelledby="b1">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">O que ele recebe</p><h2 id="b1">Cuidado que dá para ver e sentir</h2></div>
    <div class="grade3">
      <div class="card">{ico("banho")}<h3>Banho</h3><p>Produtos de qualidade e mãos qualificadas. Ele volta cheiroso, com o pelo macio e sem estresse.</p></div>
      <div class="card">{ico("tesoura")}<h3>Tosa na máquina e na tesoura</h3><p>Do acabamento prático à tosa na tesoura, sempre valorizando o jeito e o estilo do seu cão.</p></div>
      <div class="card">{ico("laco")}<h3>Enfeite de saída</h3><p>Laço, passa-fita, gravata ou bandana. Ele sai pronto para a foto.</p></div>
    </div>
  </div>
</section>

<section class="claro" aria-labelledby="b2">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Como a gente trabalha</p><h2 id="b2">Medo e agitação não são problema</h2>
      <p>Muitos cães têm dificuldade no banho: o barulho do secador, a água, ser segurado. A equipe é preparada para lidar com isso com paciência e técnica.</p></div>
    <ol class="passos">
      <li><h3>Chegada e leitura</h3><p>Antes de começar, a gente observa como ele está: confiante, ansioso, com medo do secador.</p></li>
      <li><h3>Manejo respeitoso</h3><p>Técnicas que deixam o cão mais seguro durante o banho e a tosa, sem pressa e sem brigar com ele.</p></li>
      <li><h3>Acabamento e entrega</h3><p>Conferimos cada detalhe e entregamos um cão cheiroso, bonito e tranquilo.</p></li>
    </ol>
  </div>
</section>

<section aria-labelledby="b3">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Onde fica</p><h2 id="b3">Unidade 1, na Av. Nossa Senhora de Fátima</h2></div>
    <div class="duas">
      {cartao_unidade("banho", capa_unidade("banho"), mapa=True)}
      <div class="bloco">
        <h3>Sem tempo de trazer?</h3>
        <p>O Taxi Dog busca o seu cão em casa, traz para o banho e leva de volta, em toda Toledo.</p>
        <p><a class="mais" href="{link('taxi-dog')}">Conhecer o Taxi Dog</a></p>
        <h3 style="margin-top:28px">Rações e produtos</h3>
        <p>A unidade também vende rações e produtos para pets.</p>
        <h3 style="margin-top:28px">Valores</h3>
        <p>Os valores dependem do serviço escolhido e são informados pela equipe.</p>
      </div>
    </div>
  </div>
</section>

<section class="claro" aria-labelledby="b4">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Perguntas frequentes</p><h2 id="b4">Antes de agendar</h2></div>
    {perguntas([
        ("Meu cão tem medo do banho. Vocês atendem?", "Atendemos. A equipe presta atenção ao comportamento de cada cão e usa um manejo adequado e respeitoso, no ritmo dele."),
        ("Vocês fazem tosa na tesoura?", "Sim. Fazemos tosa na máquina e tosa na tesoura."),
        ("Como eu agendo?", f'Pelo app Zoop, no link <a href="{ZOOP}">linktr.ee/zoop.pet</a>. A equipe confirma o horário com você.'),
        ("Quanto tempo leva?", pend("Tempo médio do banho e da tosa")),
        ("Vocês buscam e levam?", f'Sim, com o <a href="{link("taxi-dog")}">Taxi Dog</a>, em toda Toledo. É só pedir junto com o agendamento.'),
    ])}
  </div>
</section>

{chamada("Vamos deixar ele cheiroso?")}'''
    return pagina("banho-e-tosa", "Banho e tosa", "Banho e tosa em Toledo - PR, com tosa na tesoura | DaPata",
                  "Banho e tosa em Toledo - PR com tosa na máquina e na tesoura, manejo respeitoso e atenção a cães com medo. Av. Nossa Senhora de Fátima, 202.",
                  corpo, "banho.jpg", preload="banho.jpg")


def p_creche():
    corpo = f'''{topo("Creche e hotel · Unidade 2", "Creche e hotel para cães em Toledo, com segurança e descanso respeitado.",
        "De dia, atividades com interações supervisionadas. À noite, descanso num espaço organizado conforme o perfil de cada cão, com acompanhamento humano inclusive no período noturno.",
        img("creche.jpg", "Dois goldens no pátio ensolarado da creche", "foto", lazy=False, prioridade=True, pos="center 30%"))}

<section id="creche" aria-labelledby="c1">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Creche canina</p><h2 id="c1">Um dia com atividade e descanso</h2>
      <p>Atividades em grupo ou individuais, conforme o perfil do cão, sempre com supervisão.</p></div>
    <div class="grade3">
      <div class="card">{ico("sol")}<h3>Manhã</h3><p>Atividades externas, sol e descanso.</p></div>
      <div class="card">{ico("casa")}<h3>Tarde</h3><p>Relaxamento no espaço interno e brincadeiras na área externa.</p></div>
      <div class="card">{ico("folha")}<h3>Enriquecimento</h3><p>Piscina, chafariz, frutas congeladas e atividades sensoriais para estímulos físicos e mentais.</p></div>
    </div>
  </div>
</section>

<section class="claro" id="hotel" aria-labelledby="c2">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Hotel para cães</p><h2 id="c2">Segurança vem antes da aparência</h2></div>
    <div class="grade">
      <div class="card destaque">{ico("lua")}<h3>Descanso respeitado</h3><p>Os espaços são organizados conforme o perfil, a necessidade de tranquilidade e a segurança de cada cão. A acomodação pode ser individual ou compartilhada.</p></div>
      <div class="card">{ico("escudo")}<h3>Acompanhamento humano</h3><p>Durante toda a hospedagem, inclusive no período noturno.</p></div>
      <div class="card">{ico("grupo")}<h3>Interações supervisionadas</h3><p>A convivência é acompanhada pela equipe. Cães com dificuldade de socialização têm liberdade controlada e supervisionada.</p></div>
      <div class="card">{ico("camera")}<h3>Você acompanha de longe</h3><p>Fotos e vídeos no grupo de WhatsApp dos tutores.</p></div>
    </div>
  </div>
</section>

<section aria-labelledby="c3">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Um dia na creche</p><h2 id="c3">A turma aprova</h2></div>
    {mosaico()}
  </div>
</section>

<section class="areia" id="participar" aria-labelledby="c4">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Antes da primeira visita</p><h2 id="c4">Adaptação e regras</h2>
      <p>As regras existem para a segurança do seu cão e dos outros. A adaptação é um processo gradual, com avaliação e controle das interações.</p></div>
    <div class="rotina">
      <div class="checklist"><h3>Exigências de saúde</h3>{REQUISITOS}</div>
      <div class="bloco"><h3>Bom saber</h3>{BOM_SABER}</div>
    </div>
    <div class="duas" style="margin-top:20px">
      <div class="bloco"><h3>O que levar para o hotel</h3><ul class="lista">
        <li>Ração suficiente para a estadia.</li>
        <li>Tapete higiênico (se não levar, é cobrado à parte).</li>
        <li>Não precisa levar potes, cama, coberta nem brinquedos.</li>
      </ul></div>
      <div class="bloco"><h3>Entrada e saída do hotel</h3>
        <p>Seg a sex, 8h às 12h e 13h30 às 18h30 · Sáb, 8h às 12h.</p>
        <p style="margin-top:10px">Sábado e domingo, das 13h30 às 18h30, há plantão com agendamento prévio e taxa adicional. A equipe informa os valores.</p></div>
    </div>
  </div>
</section>

<section aria-labelledby="c5">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Onde fica</p><h2 id="c5">Unidade 2, na Av. Senador Atílio Fontana</h2></div>
    <div class="duas">
      {cartao_unidade("creche", capa_unidade("creche"), completo=True, mapa=True)}
      <div class="bloco">
        <h3>Taxi Dog</h3>
        <p>Busca e leva o seu cão para a creche ou o hotel, em toda Toledo.</p>
        <p><a class="mais" href="{link('taxi-dog')}">Conhecer o Taxi Dog</a></p>
        <h3 style="margin-top:28px">Valores</h3>
        <p>Os valores são informados pela equipe, conforme o serviço e o período.</p>
      </div>
    </div>
  </div>
</section>

<section class="claro" aria-labelledby="c6">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Perguntas frequentes</p><h2 id="c6">Antes de reservar</h2></div>
    {perguntas([
        ("Meu cão não é castrado. Ele pode vir?", "Pode. A castração é recomendada, não obrigatória. Dependendo do comportamento e da convivência, ele pode precisar ficar separado dos demais."),
        ("Meu cão tem dificuldade de socialização.", "Trabalhamos com liberdade controlada e supervisionada, preservando a segurança física dele e dos outros cães. A adaptação é gradual."),
        ("Os cães ficam todos juntos?", "Não necessariamente. A organização dos espaços considera o perfil, a necessidade de tranquilidade e a segurança de cada cão."),
        ("Vou conseguir ver como ele está?", "Sim. Mandamos fotos e vídeos no grupo de WhatsApp dos tutores."),
        ("Como reservo?", f'Pelo app Zoop, no link <a href="{ZOOP}">linktr.ee/zoop.pet</a>. A equipe confirma a reserva com você.'),
    ])}
  </div>
</section>

{chamada("Vamos planejar a estadia dele?")}'''
    return pagina("creche-e-hotel", "Creche e hotel", "Creche e hotel para cães em Toledo - PR | DaPata",
                  "Creche e hotel para cães em Toledo - PR: adaptação gradual, interações supervisionadas, piscina, chafariz e acompanhamento humano inclusive à noite.",
                  corpo, "creche.jpg", preload="creche.jpg")


def p_adestramento():
    arte = (img(FOTOS["treino"][0], FOTOS["treino"][1], "foto", lazy=False, prioridade=True) if tem_foto("treino")
            else img("adest.jpg", "Cão sentado olhando atento para o treinador", "foto", lazy=False, prioridade=True, pos="center 30%"))
    corpo = f'''{topo("Adestramento · Unidade 2", "Adestramento de cães em Toledo, com foco no vínculo.",
        "Dez anos de experiência em comportamento canino. O trabalho parte das necessidades do cão e do tutor e desenvolve obediência, foco, comunicação e convivência.",
        arte, botoes=f'<a class="btn btn-pri" href="{zap_href()}">Falar com o adestrador</a><a class="btn btn-sec" href="#formatos">Ver formatos</a>')}

<section id="formatos" aria-labelledby="a1">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Formatos</p><h2 id="a1">O treino que cabe na sua rotina</h2></div>
    <div class="grade3">
      <div class="card destaque">{ico("medalha")}<h3>Escolinha de adestramento</h3><p>Seu cão treina com a gente na unidade 2, duas vezes por semana.</p>
        <ul><li>Obediência, foco e convivência</li><li>Taxi Dog disponível para levar e trazer</li></ul></div>
      <div class="card">{ico("casa2")}<h3>Atendimento na sua casa</h3><p>Treino prático, focado no que o seu cão mais precisa. O treinador mostra, você aplica, e o suporte continua pelo WhatsApp.</p>
        <ul><li>De 40 minutos a 1 hora, ou o necessário</li><li>Você participa de tudo</li></ul></div>
      <div class="card">{ico("doc")}<h3>Consultoria comportamental</h3><p>Visita para entender o caso a fundo. Depois você recebe um protocolo de treino por escrito e orientação para continuar em casa.</p>
        <ul><li>Avaliação na residência</li><li>Protocolo escrito</li></ul></div>
    </div>
  </div>
</section>

<section class="claro" aria-labelledby="a2">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">No que a gente ajuda</p><h2 id="a2">Do básico ao comportamento mais difícil</h2></div>
    <div class="duas">
      <div class="bloco"><h3>Rotina de casa</h3><ul class="lista">
        <li>Fazer as necessidades no lugar certo</li><li>Parar de pular nas pessoas</li><li>Não fugir pelo portão</li><li>Passear sem puxar a guia</li>
      </ul></div>
      <div class="bloco"><h3>Comportamento</h3><ul class="lista">
        <li>Ansiedade</li><li>Destruição de objetos</li><li>Agressividade</li><li>Outros casos avaliados na consultoria</li>
      </ul></div>
    </div>
  </div>
</section>

<section aria-labelledby="a3">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Como funciona</p><h2 id="a3">Do primeiro contato ao cão parceiro</h2></div>
    <ol class="passos">
      <li><h3>Conversa</h3><p>Você conta o que está acontecendo e o que espera do seu cão.</p></li>
      <li><h3>Plano de treino</h3><p>A gente indica o formato e define os objetivos para o caso dele.</p></li>
      <li><h3>Treino no dia a dia</h3><p>Exercícios que entram na rotina da casa, não só na hora da aula.</p></li>
      <li><h3>Continuidade</h3><p>Orientação e suporte para manter o treino em casa.</p></li>
    </ol>
  </div>
</section>

<section class="sobre" aria-labelledby="a4">
  <div class="wrap">
    <div class="retrato">{img(FOTOS["equipe"][0], FOTOS["equipe"][1], "foto-retrato") if tem_foto("equipe") else simbolo()}</div>
    <div>
      <p class="kicker">Nosso método</p>
      <h2 id="a4">Vínculo antes de comando</h2>
      <p>O DaPata trabalha com adestramento desde 2016. A base é o vínculo: o cão aprende melhor quando confia em quem ensina e entende o que está sendo pedido.</p>
      <p>Por isso o tutor participa do processo. Cada plano considera as necessidades individuais do cão e da família.</p>
    </div>
  </div>
</section>

<section class="claro" aria-labelledby="a5">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Perguntas frequentes</p><h2 id="a5">Antes de começar</h2></div>
    {perguntas([
        ("Eu preciso participar do treino?", "Sim, e isso faz diferença. O treinador mostra e você aprende a aplicar, para o cão responder a você no dia a dia."),
        ("Qual formato é melhor para o meu cão?", "Depende do caso. A gente orienta na primeira conversa, considerando o que você precisa e o perfil do cão."),
        ("Quanto custa?", "Os valores dependem do formato e são informados pela equipe."),
        ("Tem idade mínima?", pend("Idade mínima e requisitos para o adestramento")),
    ])}
  </div>
</section>

{chamada("Vamos conversar sobre o seu cão?", "Conte o que está acontecendo e a gente indica o melhor caminho.")}'''
    return pagina("adestramento", "Adestramento", "Adestramento de cães em Toledo - PR | DaPata",
                  "Adestramento de cães em Toledo - PR desde 2016: escolinha duas vezes por semana, atendimento em casa e consultoria comportamental com protocolo escrito.",
                  corpo, "adest.jpg", preload=None if tem_foto("treino") else "adest.jpg")


def p_taxi():
    corpo = f'''{topo("Taxi Dog", "Taxi Dog em Toledo: ele vai e volta com segurança.",
        "A gente busca o seu cão em casa e leva de volta depois do banho, da creche, do hotel ou do adestramento. Atendemos toda Toledo, só para os serviços do DaPata.",
        foto("taxi", "Foto do carro do Taxi Dog", lazy=False))}

<section aria-labelledby="t1">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Segurança em primeiro lugar</p><h2 id="t1">Pensado para o conforto dele</h2></div>
    <div class="grade">
      <div class="card">{ico("neve")}<h3>Ar-condicionado</h3><p>Temperatura agradável durante a viagem, mesmo nos dias quentes.</p></div>
      <div class="card">{ico("caixa")}<h3>Caixas apropriadas</h3><p>Os cães viajam em caixas de transporte e com organização segura dentro do veículo.</p></div>
      <div class="card">{ico("pin")}<h3>Toda Toledo</h3><p>Atendemos todos os bairros da cidade.</p></div>
      <div class="card">{ico("rota")}<h3>Só para os serviços DaPata</h3><p>O transporte leva e traz o seu cão para banho e tosa, creche, hotel e adestramento.</p></div>
    </div>
  </div>
</section>

<section class="claro" aria-labelledby="t2">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">Como pedir</p><h2 id="t2">Três passos</h2></div>
    <ol class="passos">
      <li><h3>Agende o serviço</h3><p>Banho e tosa, creche, hotel ou adestramento, pelo app Zoop.</p></li>
      <li><h3>Peça o Taxi Dog</h3><p>Avise se é só ida, só volta ou ida e volta.</p></li>
      <li><h3>A equipe confirma</h3><p>Os horários de busca e entrega são confirmados pela equipe com você.</p></li>
    </ol>
  </div>
</section>

<section aria-labelledby="t3">
  <div class="wrap">
    <div class="duas">
      <div class="bloco"><h3 id="t3">Valores</h3><p>O valor do Taxi Dog é informado pela equipe no agendamento.</p></div>
      <div class="bloco"><h3>Saída</h3><p>O carro sai da unidade 2, na {UNIDADES["creche"]["rua"]}.</p></div>
    </div>
  </div>
</section>

{chamada("Quer que a gente busque?")}'''
    return pagina("taxi-dog", "Taxi Dog", "Taxi Dog em Toledo - PR, transporte de cães | DaPata",
                  "Taxi Dog do DaPata em toda Toledo - PR: transporte do seu cão para banho, creche, hotel e adestramento, com ar-condicionado e caixas de transporte.",
                  corpo)


def p_quem():
    resp = simbolo()
    equipe = (img(FOTOS["equipe"][0], FOTOS["equipe"][1], "foto", estilo="aspect-ratio:16/9;border-radius:28px") if tem_foto("equipe")
              else foto_pend("equipe", "Foto da equipe"))
    corpo = f'''<section class="sobre topo-sobre" aria-labelledby="q0">
  <div class="wrap">
    <div class="retrato">{resp}</div>
    <div>
      <p class="kicker">Quem somos</p>
      <h1 id="q0">Da pata ao coração.</h1>
      <p class="lead">O DaPata nasceu do amor pelos animais e da vontade de fazer diferente: um ambiente que transmita vínculo, amizade e segurança.</p>
    </div>
  </div>
</section>

<section aria-labelledby="q1">
  <div class="wrap duas" style="align-items:center;gap:56px">
    <div>
      <p class="kicker">A nossa história</p>
      <h2 id="q1">Tudo começou com o adestramento</h2>
      <p>Começamos com o adestramento, em 2016. Com o tempo, o trabalho cresceu e vieram o pet shop e a hotelaria. {pend("Ano da expansão")}</p>
      <p style="margin-top:1em">Hoje são duas unidades em Toledo: uma de banho e tosa e outra de creche, hotel e adestramento.</p>
      <p style="margin-top:1em">A experiência em comportamento canino continua sendo a base: no jeito de conduzir um cão no banho, de organizar a rotina da creche, de pensar o descanso no hotel.</p>
    </div>
    {img("g1.jpg", "Pátio da creche do DaPata, com dois buldogues franceses e a placa da empresa", "foto", estilo="aspect-ratio:4/4.6;object-fit:cover;width:100%;border-radius:28px 28px 28px 110px", pos="center 55%")}
  </div>
</section>

<section class="claro" aria-labelledby="q2">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">No que a gente acredita</p><h2 id="q2">O que guia cada atendimento</h2></div>
    <div class="grade">
      <div class="dif"><div class="num">01</div><h3>Atendimento personalizado</h3><p>Cada cão e cada tutor têm características e necessidades próprias, e o atendimento parte delas.</p></div>
      <div class="dif"><div class="num">02</div><h3>Respeito ao animal</h3><p>Manejo cuidadoso e atenção ao comportamento em todos os serviços.</p></div>
      <div class="dif"><div class="num">03</div><h3>Segurança</h3><p>Em cada interação, cada espaço e cada viagem do Taxi Dog.</p></div>
      <div class="dif"><div class="num">04</div><h3>Vínculo</h3><p>Um lugar onde cada momento fortalece laços infinitos de amor e cuidado.</p></div>
    </div>
  </div>
</section>

<section aria-labelledby="q3">
  <div class="wrap">
    <div class="cabeca"><p class="kicker">A família da casa</p><h2 id="q3">Quem você vai encontrar por aqui</h2></div>
    {equipe}
    <div class="grade" style="margin-top:20px">
      <div class="card"><h3>Diamante</h3><p>Vira-lata veterano que mora no DaPata.</p></div>
      <div class="card"><h3>Belchior</h3><p>Border collie da casa, especialista em truques.</p></div>
    </div>
  </div>
</section>

{chamada("Venha conhecer", "Fale com a equipe ou agende o primeiro serviço do seu cão.")}'''
    return pagina("quem-somos", "Quem somos", "Quem somos: a história do DaPata Pet Center em Toledo - PR",
                  "Conheça o DaPata Pet Center, em Toledo - PR: história iniciada com o adestramento em 2016, base em comportamento canino e atendimento personalizado.",
                  corpo, "g1.jpg")


def p_unidades():
    corpo = f'''<section class="pagina-topo">
  <div class="wrap so-texto">
    <div><p class="kicker">Unidades e contato</p><h1>Duas unidades em Toledo</h1>
      <p class="lead">Uma para banho e tosa, outra para creche, hotel e adestramento. As duas vendem rações e produtos para pets, e o WhatsApp atende as duas.</p></div>
  </div>
</section>

<section class="sem-topo" aria-labelledby="u1">
  <h2 id="u1" class="sr">Endereços e horários</h2>
  <div class="wrap unidades">
    {cartao_unidade("banho", capa_unidade("banho"), completo=True, mapa=True)}
    {cartao_unidade("creche", capa_unidade("creche"), completo=True, mapa=True)}
  </div>
</section>

{chamada("Fale com a gente", "Escolha o canal que preferir. O agendamento é feito pelo Zoop.", com_canais=True)}'''
    return pagina("unidades", "Unidades e contato", "Unidades, horários e contato | DaPata Pet Center em Toledo - PR",
                  "Endereços, horários e contato das duas unidades do DaPata Pet Center em Toledo - PR: banho e tosa, creche, hotel e adestramento.",
                  corpo)


def p_404():
    corpo = f'''<section class="chamada" style="padding:120px 0">
  <div class="wrap">
    <p class="kicker">Página não encontrada</p>
    <h1>Essa pegada sumiu.</h1>
    <p style="margin-top:1em">O endereço pode ter mudado. Que tal voltar para o início?</p>
    <div class="acoes"><a class="btn btn-pri" href="{link('index')}">Ir para o início</a><a class="btn btn-sec" href="{link('unidades')}">Ver unidades e contato</a></div>
  </div>
</section>'''
    return pagina("404", "Página não encontrada", "Página não encontrada | DaPata Pet Center", "Página não encontrada.", corpo)


PAGINAS = {"index": p_index, "banho-e-tosa": p_banho, "creche-e-hotel": p_creche,
           "adestramento": p_adestramento, "taxi-dog": p_taxi, "quem-somos": p_quem,
           "unidades": p_unidades, "404": p_404}


# ---------------------------------------------------------------- pós-processamento
_EXT = re.compile(r'(<a\b[^>]*?href="(https?://[^"]+)"[^>]*)>(.*?)</a>', re.S)


def externos(html):
    """Links externos abrem em nova aba, com rel de segurança e aviso para leitor de tela."""
    def f(m):
        tag, conteudo = m.group(1), m.group(3)
        if "target=" not in tag:
            tag += ' target="_blank" rel="noopener noreferrer"'
        return f'{tag}>{conteudo}<span class="sr"> (abre em nova aba)</span></a>'
    return _EXT.sub(f, html)


def webp():
    """Gera .webp ao lado de cada .jpg (qualidade 82), só quando o jpg for mais novo."""
    from PIL import Image
    for jpg in IMG.glob("*.jpg"):
        w = jpg.with_suffix(".webp")
        if not w.exists() or w.stat().st_mtime < jpg.stat().st_mtime:
            with Image.open(jpg) as im:
                im.convert("RGB").save(w, "WEBP", quality=82, method=6)


def logo_png():
    """PNG do logo para o schema/Google (gerado uma vez a partir do SVG, se o rsvg estiver disponível)."""
    destino = IMG / "logo-dapata.png"
    if destino.exists():
        return
    sprite = (IMG / "marca.svg").read_text()
    m = re.search(r'<symbol id="logo" viewBox="([^"]+)">(.*?)</symbol>', sprite, re.S)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{m.group(1)}" width="1200">'
           + m.group(2).replace("currentColor", "#FF6410") + "</svg>")
    tmp = ROOT / "logo-tmp.svg"
    tmp.write_text(svg)
    try:
        subprocess.run(["rsvg-convert", "-w", "1200", str(tmp), "-o", str(destino)], check=True)
    except Exception:
        try:
            import cairosvg
            cairosvg.svg2png(url=str(tmp), write_to=str(destino), output_width=1200)
        except Exception:
            print("aviso: não consegui gerar logo-dapata.png")
    tmp.unlink(missing_ok=True)


def gerar(destino: Path):
    for slug, fn in PAGINAS.items():
        html = externos(fn())
        if not PREVIA:
            # em produção os recursos ficam na raiz
            for a in ('href="css/', 'href="img/', 'src="img/', 'srcset="img/', 'href="favicon', 'src="js/', 'data-arquivo="img/'):
                html = html.replace(a, a.replace('"', '"/', 1))
        (destino / f"{slug}.html").write_text(html, encoding="utf-8")
    if not PREVIA:
        urls = "".join(f"<url><loc>{BASE_URL}{'/' if s == 'index' else '/' + s}</loc></url>"
                       for s in PAGINAS if s != "404")
        (destino / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
        (destino / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n")


if __name__ == "__main__":
    webp()
    logo_png()
    if "--previa" in sys.argv:
        PREVIA = True
        dest = Path(sys.argv[sys.argv.index("--previa") + 1])
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(SITE, dest, ignore=shutil.ignore_patterns("*.html", "sitemap.xml", "robots.txt"))
        gerar(dest)
        print("prévia em", dest)
    else:
        gerar(SITE)
        print("site gerado em", SITE)
