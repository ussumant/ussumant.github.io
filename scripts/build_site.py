#!/usr/bin/env python3
"""Build the checked-in static site from content/site.json."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
SITE = DATA["site"]
WORK = DATA["work"]
READING = DATA.get("reading", [])
SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def absolute(path: str) -> str:
    return f"{SITE['url']}{path}"


def head(title: str, description: str, path: str, *, typing: bool = False) -> str:
    canonical = absolute(path)
    typing_init = "  <script>document.documentElement.classList.add('js-typing');</script>\n" if typing else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{typing_init}  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{e(canonical)}">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%A5%8A%3C/text%3E%3C/svg%3E">
  <link rel="alternate" type="application/atom+xml" title="Sumant — recent work" href="/feed.xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@400..700&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{e(canonical)}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:image" content="{e(absolute('/og.png'))}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(description)}">
  <meta name="twitter:image" content="{e(absolute('/og.png'))}">
</head>"""


def wordmark(*, heading: bool = False) -> str:
    tag = "h1" if heading else "p"
    typing_attr = " data-typing-logo" if heading else ""
    return f'<{tag} class="wordmark"{typing_attr}><a href="/">sumant</a></{tag}>'


def footer(*, copyright: bool = True) -> str:
    socials = " · ".join(
        f'<a href="{e(item["url"])}" rel="me noopener">{e(item["label"].lower())}</a>'
        for item in SITE["social"]
    )
    copyright_line = f'  <p class="copyright">© 2026 Sumant · {e(SITE["location"])}</p>\n' if copyright else ""
    return f"""<footer class="site-footer">
  <p>Contact:<br>{socials} · <a href="/reading/">reading</a> · <a href="/feed.xml">rss</a></p>
{copyright_line}</footer>"""


def project_item(item: dict, *, include_meta: bool = False) -> str:
    meta = f' <span class="project-meta">({e(item["stage"].lower())} · {e(item["period"])})</span>' if include_meta else ""
    summary = item["summary"] if include_meta else item.get("home_summary", item["summary"])
    return (
        f'<li><span aria-hidden="true">{e(item["emoji"])}</span> '
        f'<a class="live" href="/work/{e(item["slug"])}/">{e(item["display"])}</a> '
        f'— {e(summary)}{meta}</li>'
    )


def render_reel() -> str:
    return """<div class="reel-thumb" id="reelThumb" role="button" tabindex="0" aria-label="Play Muay Thai reel">
  <video id="reelVideo" src="/muay-thai-demo.mp4?v=2" poster="/poster.jpg?v=1" muted loop autoplay playsinline preload="metadata"></video>
</div>
<div class="reel-lightbox" id="reelLightbox" aria-hidden="true">
  <div class="reel-backdrop" id="reelBackdrop"></div>
  <div class="reel-stage" id="reelStage">
    <div class="reel-controls">
      <span class="reel-time" id="reelTime">0:00 / 0:00</span>
      <span class="reel-actions"><span class="esc-hint">esc to close</span><button class="reel-btn" id="reelRestart" type="button">Restart</button></span>
    </div>
  </div>
</div>"""


def render_home() -> str:
    current_slug = DATA["now"]["work_slug"]
    featured = "".join(
        project_item(item)
        for item in WORK
        if item["featured"] and item["slug"] != current_slug
    )
    updates = []
    for item in DATA["updates"]:
        external = f' · <a href="{e(item["external_url"])}" rel="noopener">artifact ↗</a>' if item.get("external_url") else ""
        updates.append(f"""<li>
  <time datetime="{e(item['date'])}">{e(item['date_label'])}</time><br>
  <a class="live" href="/work/{e(item['work_slug'])}/">{e(item['title'])}</a> — {e(item['body'])}
  <span class="update-links">{external}</span>
</li>""")
    about = "".join(f"<p>{e(paragraph)}</p>" for paragraph in DATA["about"])
    side = DATA["side_quest"]
    return "".join([
        head(SITE["title"], SITE["description"], "/", typing=True),
        '<body class="home-page"><a class="skip-link" href="#main">Skip to content</a>',
        '<main id="main" tabindex="-1">',
        '<section class="home-scene" aria-label="Introduction">',
        wordmark(heading=True),
        f'<p class="intro">{e(DATA["hero"]["title"])}</p>',
        f'<p class="intro">Before this I co-founded CustomerGlu and built its gamification SDK from scratch — it reached 150M+ devices.</p>',
        f'<p class="now-line" id="now"><span class="live-dot" aria-hidden="true"></span><a class="live" href="/work/{e(DATA["now"]["work_slug"])}/">{e(DATA["now"]["label"].lower())}</a> — {e(DATA["now"]["title"])}. {e(DATA["work"][0]["summary"])}</p>',
        f'<ul class="project-list" id="work">{featured}</ul>',
        '<p class="small-link"><a class="live" href="/work/">all work →</a> · <a class="live" href="/reading/">reading →</a></p>',
        f'<p class="intro">{e(SITE["location"])}.</p>',
        '<p>Contact:<br><a class="live" href="https://github.com/ussumant" rel="me noopener">github</a> · <a class="live" href="https://x.com/sumant_us" rel="me noopener">x</a> · <a class="live" href="https://www.linkedin.com/in/sumantus/" rel="me noopener">linkedin</a></p>',
        render_reel(),
        f'''<figure class="charm">
  <a class="gif-link" href="https://github.com/ussumant/muay-thai" rel="noopener"><img class="gifimg" src="{e(side['image'])}" alt="{e(side['alt'])}" width="460" height="252"></a>
  <figcaption>🥊 <a href="https://github.com/ussumant/muay-thai" rel="noopener">sofia vs sumant</a> — best of 3</figcaption>
  <p class="copyright">© 2026 Sumant</p>
</figure>''',
        '</section>',
        f'''<section class="home-section" id="updates" aria-labelledby="updates-title">
  <h2 id="updates-title">recently</h2>
  <p class="section-note">A small reverse-chronological shipping log. Updated {e(SITE['updated_label'])}. <a href="/feed.xml">rss ↗</a></p>
  <ol class="update-list">{''.join(updates)}</ol>
</section>''',
        f'''<section class="home-section" id="about" aria-labelledby="about-title">
  <h2 id="about-title">about</h2>
  <div class="about-copy">{about}</div>
</section>''',
        '</main><script src="/scripts/site.js"></script></body></html>\n',
    ])


def plain_open(title: str, description: str, path: str, *, body_class: str = "notes-page") -> str:
    return "".join([
        head(title, description, path),
        f'<body class="{e(body_class)}"><a class="skip-link" href="#main">Skip to content</a>',
        f'<header class="plain-header">{wordmark()}<a href="/">← home</a></header>',
    ])


def render_archive() -> str:
    rows = "".join(project_item(item, include_meta=True) for item in WORK)
    return "".join([
        plain_open("Work — Sumant", "Products, systems, and experiments built by Sumant.", "/work/"),
        '<main id="main" tabindex="-1">',
        '<header class="page-intro"><h1>work</h1><p>Proof, not a project inventory. Each note records what I built and the honest stage it reached.</p></header>',
        f'<ul class="project-list archive-list">{rows}</ul>',
        '</main>', footer(), '</body></html>\n',
    ])


def render_detail(item: dict, next_item: dict) -> str:
    sections = "".join(
        f'<section><h2>{e(section["title"])}</h2><p>{e(section["body"])}</p></section>'
        for section in item["sections"]
    )
    links = " · ".join(
        f'<a href="{e(link["url"])}" rel="noopener">{e(link["label"])} ↗</a>'
        for link in item["links"]
    )
    links_block = f'<p class="detail-links">{links}</p>' if links else ""
    cover = item.get("cover")
    cover_block = ""
    if cover:
        cover_block = f'''<figure class="detail-media">
  <a href="{e(cover['src'])}"><img src="{e(cover['src'])}" alt="{e(cover['alt'])}" loading="eager"></a>
  <figcaption>{e(cover['caption'])} <a href="{e(cover['src'])}">Open full size ↗</a></figcaption>
</figure>'''
    return "".join([
        plain_open(f"{item['title']} — Sumant", item["summary"], f"/work/{item['slug']}/"),
        '<main id="main" tabindex="-1"><article class="detail">',
        f'''<header class="detail-header">
  <a class="breadcrumb" href="/work/">← work / {e(item['order'])}</a>
  <p class="detail-meta">{e(item['stage'].lower())} · {e(item['period'])}</p>
  <h1>{e(item['title'])}</h1>
  <p class="detail-lead">{e(item['lead'])}</p>
</header>
{cover_block}
<dl class="meta-list">
  <div><dt>role</dt><dd>{e(item['role'])}</dd></div>
  <div><dt>fields</dt><dd>{e(' · '.join(item['tags']))}</dd></div>
</dl>
<div class="detail-body">{sections}{links_block}</div>
<p class="next-work"><span>next note:</span><br><a class="live" href="/work/{e(next_item['slug'])}/">{e(next_item['display'])} →</a></p>''',
        '</article></main>', footer(), '</body></html>\n',
    ])


def reading_item(item: dict) -> str:
    tags = " · ".join(e(tag) for tag in item["tags"])
    links = f'<a class="live" href="/reading/{e(item["slug"])}/">read note →</a>'
    if item.get("source_url"):
        links += f' · <a href="{e(item["source_url"])}" rel="noopener">paper ↗</a>'
    if item.get("repo_url"):
        links += f' · <a href="{e(item["repo_url"])}" rel="noopener">repo ↗</a>'
    return f'''<li class="reading-item">
  <p class="reading-item-meta">{e(item["status"].lower())} · {e(item["period"])} · {e(item["venue"])}</p>
  <h2><a href="/reading/{e(item['slug'])}/">{e(item["display"])}</a></h2>
  <p>{e(item["summary"])}</p>
  <p class="reading-item-links">{links}</p>
  <p class="reading-tags">{tags}</p>
</li>'''


def render_reading_archive() -> str:
    rows = "".join(reading_item(item) for item in READING)
    return "".join([
        plain_open("Reading — Sumant", "Papers Sumant is reading, with notes on what they make possible.", "/reading/", body_class="notes-page reading-page reading-index"),
        '<main id="main" tabindex="-1">',
        '<header class="page-intro"><h1>reading</h1><p>Papers I am reading to understand products, behavior, and AI systems. The notes are working interpretations, not paper abstracts.</p></header>',
        f'<ul class="reading-list">{rows}</ul>',
        '</main>', footer(), '</body></html>\n',
    ])


def render_reading_orientation(item: dict) -> str:
    use_cases = "".join(
        f'<li><strong>{e(use_case["label"])}</strong><span>{e(use_case["body"])}</span></li>'
        for use_case in item["use_cases"]
    )
    return f'''<section class="reading-orientation" aria-labelledby="reading-orientation-title">
  <div class="reading-tldr"><p class="reading-label">TL;DR</p><h2 id="reading-orientation-title">{e(item["takeaway"])}</h2><p>{e(item["tldr"])}</p></div>
  <div class="reading-use-cases"><p class="reading-label">WHERE THIS BECOMES USEFUL</p><ul>{use_cases}</ul></div>
</section>'''


def render_reading_story(item: dict) -> str:
    scenes = "".join(
        f'''<li class="reading-scene"><div class="reading-scene-time">{e(scene["time"])}</div><div class="reading-scene-marker" aria-hidden="true"><span></span></div><div class="reading-scene-copy"><h3>{e(scene["title"])}</h3><p>{e(scene["body"])}</p><small>{e(scene["signal"])}</small></div></li>'''
        for scene in item["story"]["scenes"]
    )
    return f'''<section class="reading-story-section" aria-labelledby="reading-story-title">
  <div class="reading-story-head"><p class="reading-label">START WITH THE FEELING</p><h2 id="reading-story-title">{e(item["story"].get("section_headline", "Follow the day."))}</h2><p>{e(item["story"]["intro"])}</p></div>
  <div class="reading-story-grid">
    <ol class="reading-scene-list">{scenes}</ol>
    <div class="reading-town-stage" role="img" aria-label="A simple map of Smallville with Isabella's house, Maria's house, the cafe, and the party as an idea moves through the town.">
      <div class="reading-town-top"><strong>SMALLVILLE</strong><span>DAY 02 / PARTY DAY</span></div>
      <div class="reading-town-map" aria-hidden="true"><span class="reading-town-route reading-town-route-one"></span><span class="reading-town-route reading-town-route-two"></span><span class="reading-town-route reading-town-route-three"></span><div class="reading-town-place reading-town-house"><strong>Isabella’s house</strong><small>the idea starts here</small></div><div class="reading-town-place reading-town-cafe"><strong>the café</strong><small>people cross paths</small></div><div class="reading-town-place reading-town-party"><strong>the party</strong><small>6:00 pm</small></div><span class="reading-town-person reading-town-person-isabella">I</span><span class="reading-town-person reading-town-person-maria">M</span><span class="reading-town-person reading-town-person-sam">S</span></div>
      <div class="reading-town-bottom"><strong>One plan becomes many possibilities.</strong><span>The world is the part that pushes back.</span></div>
    </div>
  </div>
</section>'''


def render_reading_principles(item: dict) -> str:
    signals = ["world", "view", "memory", "choice", "consequence"]
    principles = "".join(
        f'<li><span class="reading-principle-number">{e(principle["number"])}</span><div><h3>{e(principle["title"])}</h3><p>{e(principle["body"])}</p></div><small>{signals[index]}</small></li>'
        for index, principle in enumerate(item["principles"])
    )
    return f'''<section class="reading-principles-section" aria-labelledby="reading-principles-title">
  <div class="reading-principles-head"><p class="reading-label">FIRST PRINCIPLES</p><h2 id="reading-principles-title">What must be true before a world can behave?</h2><p>Strip away the language model for a moment. These are the basic conditions that make a simulated life possible.</p></div>
  <ol class="reading-principle-list">{principles}</ol>
</section>'''


def render_reading_build(item: dict) -> str:
    steps = "".join(
        f'<li><span class="reading-build-number">{e(step["number"])}</span><div><h3>{e(step["title"])}</h3><p>{e(step["body"])}</p></div></li>'
        for step in item["build_steps"]
    )
    return f'''<section class="reading-build-section" aria-labelledby="reading-build-title">
  <div class="reading-subhead"><span class="reading-index">06</span><div><h2 id="reading-build-title">How we would build it.</h2><p>Start with a world that works. Add intelligence only where it helps us see behavior change.</p></div></div>
  <ol class="reading-build-list">{steps}</ol>
  <div class="reading-build-stop"><p class="reading-label">STOP HERE FIRST</p><p>If we cannot explain one surprising action from a person’s memories, goals, and surroundings, we should not add more people or more features.</p></div>
</section>'''


def render_reading_loop() -> str:
    return '''<section class="reading-subsection" aria-labelledby="reading-loop-title">
  <div class="reading-subhead"><span class="reading-index">01</span><div><h2 id="reading-loop-title">The architecture is the argument.</h2><p>The paper’s key move is a loop around the language model: keep a record, choose what matters, make meaning, make a plan, act, and observe the consequences.</p></div></div>
  <div class="reading-loop-grid">
    <div class="reading-diagram reading-loop-diagram">
      <svg class="reading-svg" viewBox="0 0 840 360" role="img" aria-labelledby="loop-svg-title loop-svg-desc">
        <title id="loop-svg-title">Generative agent architecture loop</title>
        <desc id="loop-svg-desc">An agent perceives the world, stores observations in memory, retrieves relevant memories, and acts. Retrieved memories also feed planning and reflection, which return to memory.</desc>
        <defs><marker id="reading-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#1a52e0"/></marker><marker id="reading-arrow-orange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#d66b2f"/></marker></defs>
        <rect x="177" y="50" width="436" height="272" rx="3" fill="#f5f7ff" stroke="#1a52e0" stroke-dasharray="7 6"/>
        <text x="197" y="74" class="reading-svg-mono" font-size="10" fill="#1a52e0">GENERATIVE AGENT MEMORY</text>
        <path d="M 153 190 H 195" class="reading-flow-edge" marker-end="url(#reading-arrow)"/>
        <path d="M 324 190 H 366" class="reading-flow-edge" marker-end="url(#reading-arrow)"/>
        <path d="M 492 190 H 633" class="reading-flow-edge" marker-end="url(#reading-arrow)"/>
        <path d="M 429 153 V 111" class="reading-flow-edge" marker-end="url(#reading-arrow)"/>
        <path d="M 429 227 V 270" class="reading-flow-edge" marker-end="url(#reading-arrow)"/>
        <path d="M 366 296 H 290 Q 258 296 258 266 V 225" class="reading-flow-edge reading-flow-edge-return" marker-end="url(#reading-arrow-orange)"/>
        <path d="M 492 111 H 548 Q 576 111 576 141 V 153" class="reading-flow-edge reading-flow-edge-return" marker-end="url(#reading-arrow-orange)"/>
        <path d="M 680 163 C 758 105 740 43 650 42 C 576 40 523 48 478 66" class="reading-flow-edge reading-flow-edge-loop" marker-end="url(#reading-arrow-orange)"/>
        <g class="reading-arch-node" data-reading-node="observe"><rect x="37" y="160" width="116" height="60" rx="3" fill="#fff" stroke="#1a52e0"/><text x="95" y="184" text-anchor="middle" class="reading-svg-label" font-size="15" font-weight="700">Observe</text><text x="95" y="203" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#666">what happened?</text></g>
        <g class="reading-arch-node" data-reading-node="memory"><rect x="195" y="160" width="129" height="60" rx="3" fill="#fff" stroke="#1a52e0"/><text x="259" y="184" text-anchor="middle" class="reading-svg-label" font-size="15" font-weight="700">Memory stream</text><text x="259" y="203" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#666">keep the record</text></g>
        <g class="reading-arch-node" data-reading-node="retrieve"><rect x="366" y="160" width="126" height="60" rx="3" fill="#fff" stroke="#1a52e0"/><text x="429" y="184" text-anchor="middle" class="reading-svg-label" font-size="15" font-weight="700">Retrieve</text><text x="429" y="203" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#666">what matters now?</text></g>
        <g class="reading-arch-node" data-reading-node="act"><rect x="633" y="160" width="87" height="60" rx="3" fill="#fff3ea" stroke="#d66b2f"/><text x="676" y="184" text-anchor="middle" class="reading-svg-label" font-size="15" font-weight="700">Act</text><text x="676" y="203" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#8a4a25">change world</text></g>
        <g class="reading-arch-node" data-reading-node="plan"><rect x="366" y="66" width="126" height="45" rx="3" fill="#fffdf4" stroke="#aa8b32"/><text x="429" y="85" text-anchor="middle" class="reading-svg-label" font-size="14" font-weight="700">Plan</text><text x="429" y="101" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#806b2a">shape next hours</text></g>
        <g class="reading-arch-node" data-reading-node="reflect"><rect x="366" y="270" width="126" height="45" rx="3" fill="#f1f6fb" stroke="#557c9b"/><text x="429" y="289" text-anchor="middle" class="reading-svg-label" font-size="14" font-weight="700">Reflect</text><text x="429" y="305" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#557c9b">make meaning</text></g>
        <text x="634" y="246" class="reading-svg-mono" font-size="9" fill="#d66b2f">new observations</text>
        <text x="197" y="341" class="reading-svg-mono" font-size="9" fill="#666">plans + reflections return as memories</text>
      </svg>
      <div class="reading-node-buttons" role="group" aria-label="Choose a component">
        <button class="reading-node-button" type="button" data-reading-node="observe" aria-pressed="false">observe</button><button class="reading-node-button" type="button" data-reading-node="memory" aria-pressed="false">memory</button><button class="reading-node-button" type="button" data-reading-node="retrieve" aria-pressed="true">retrieve</button><button class="reading-node-button" type="button" data-reading-node="reflect" aria-pressed="false">reflect</button><button class="reading-node-button" type="button" data-reading-node="plan" aria-pressed="false">plan</button><button class="reading-node-button" type="button" data-reading-node="act" aria-pressed="false">act</button>
      </div>
    </div>
    <aside class="reading-explainer" aria-live="polite"><p class="reading-label">SELECTED COMPONENT</p><h3 data-reading-detail-title>Retrieve what matters now.</h3><p data-reading-detail-copy>The full history is too large and too distracting to place in every prompt. Retrieval selects a compact set of memories that can inform the current decision.</p><ul data-reading-detail-list><li>Use the current situation as a query.</li><li>Balance recency, importance, and relevance.</li><li>Pass only the top-ranked memories onward.</li></ul><p class="reading-explainer-foot" data-reading-detail-foot>Attention over an external, persistent notebook.</p></aside>
  </div>
</section>'''


def render_reading_retrieval() -> str:
    return '''<section class="reading-subsection" aria-labelledby="reading-retrieval-title">
  <div class="reading-subhead"><span class="reading-index">02</span><div><h2 id="reading-retrieval-title">Memory is selective attention.</h2><p>Isabella may have thousands of observations. The question decides which few records become “present” for the next answer.</p></div></div>
  <div class="reading-retrieval-grid">
    <div class="reading-question-block"><p class="reading-label">QUESTION</p><blockquote>“What are you looking forward to the most?”</blockquote><p>The paper’s retrieval score combines three signals:</p><p class="reading-formula">recency + importance + relevance</p><p class="reading-small">The scores below are the paper’s own retrieval illustration. The bars are labeled directly so the mechanism can be read at a glance.</p></div>
    <div class="reading-ranking"><div class="reading-ranking-head"><span>candidate memories</span><span>score</span></div>
      <div class="reading-memory-row is-hit"><div><strong>planning a Valentine’s Day party</strong><small>relevant future event · high signal</small></div><div class="reading-memory-score"><b>2.34</b><span>rec .91 · imp .63 · rel .80</span><div class="reading-score-lines"><i><em>rec</em><u style="width:91%"></u></i><i><em>imp</em><u style="width:63%"></u></i><i><em>rel</em><u style="width:80%"></u></i></div></div></div>
      <div class="reading-memory-row is-hit"><div><strong>ordered decorations for the party</strong><small>recent preparation · meaningful</small></div><div class="reading-memory-score"><b>2.21</b><span>rec .87 · imp .63 · rel .71</span><div class="reading-score-lines"><i><em>rec</em><u style="width:87%"></u></i><i><em>imp</em><u style="width:63%"></u></i><i><em>rel</em><u style="width:71%"></u></i></div></div></div>
      <div class="reading-memory-row is-hit"><div><strong>researched ideas for the party</strong><small>recent preparation · related</small></div><div class="reading-memory-score"><b>2.20</b><span>rec .85 · imp .73 · rel .62</span><div class="reading-score-lines"><i><em>rec</em><u style="width:85%"></u></i><i><em>imp</em><u style="width:73%"></u></i><i><em>rel</em><u style="width:62%"></u></i></div></div></div>
      <div class="reading-memory-row is-muted"><div><strong>writing in her journal</strong><small>ordinary morning observation</small></div><div class="reading-memory-score"><b>—</b><span>not top-ranked</span></div></div>
      <div class="reading-memory-row is-muted"><div><strong>the refrigerator is idle</strong><small>environmental state</small></div><div class="reading-memory-score"><b>—</b><span>not top-ranked</span></div></div>
    </div>
  </div>
</section>'''


def render_reading_reflection() -> str:
    return '''<section class="reading-subsection" aria-labelledby="reading-reflection-title">
  <div class="reading-subhead"><span class="reading-index">03</span><div><h2 id="reading-reflection-title">Reflection turns events into identity.</h2><p>An observation records an event. A reflection turns several events into a reusable idea about a person, a relationship, or the world.</p></div></div>
  <div class="reading-diagram reading-reflection-diagram">
    <svg class="reading-svg" viewBox="0 0 840 330" role="img" aria-labelledby="reflection-svg-title reflection-svg-desc">
      <title id="reflection-svg-title">Reflection tree for Klaus Mueller</title>
      <desc id="reflection-svg-desc">Klaus's observations about reading and discussing research become increasingly abstract reflections, ending in a high-level statement about his dedication to research.</desc>
      <path d="M 129 236 C 218 236 232 196 300 196 M 129 285 C 218 285 232 213 300 196 M 392 196 C 461 196 477 157 535 157 M 392 196 C 461 196 477 236 535 236 M 392 196 C 461 196 478 90 535 90 M 630 157 C 687 157 703 115 760 105 M 630 90 C 687 90 703 104 760 105 M 630 236 C 687 236 703 140 760 105" fill="none" stroke="#8fa1ab" stroke-width="1.8"/>
      <g><rect x="39" y="215" width="180" height="42" rx="3" fill="#f4f4f4" stroke="#d7d7d7"/><text x="129" y="232" text-anchor="middle" class="reading-svg-label" font-size="11">reads about</text><text x="129" y="247" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#666">gentrification</text></g>
      <g><rect x="39" y="264" width="180" height="42" rx="3" fill="#f4f4f4" stroke="#d7d7d7"/><text x="129" y="281" text-anchor="middle" class="reading-svg-label" font-size="11">reads about</text><text x="129" y="296" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#666">urban design</text></g>
      <g><rect x="300" y="175" width="176" height="43" rx="3" fill="#f1f6fb" stroke="#557c9b"/><text x="388" y="193" text-anchor="middle" class="reading-svg-label" font-size="11">spends many hours</text><text x="388" y="208" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#557c9b">reading</text></g>
      <g><rect x="535" y="136" width="166" height="43" rx="3" fill="#f1f6fb" stroke="#557c9b"/><text x="618" y="154" text-anchor="middle" class="reading-svg-label" font-size="11">engages in</text><text x="618" y="169" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#557c9b">research activities</text></g>
      <g><rect x="535" y="215" width="166" height="43" rx="3" fill="#f1f6fb" stroke="#557c9b"/><text x="618" y="233" text-anchor="middle" class="reading-svg-label" font-size="11">talks with a librarian</text><text x="618" y="248" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#557c9b">about research</text></g>
      <g><rect x="492" y="68" width="138" height="43" rx="3" fill="#fffdf4" stroke="#aa8b32"/><text x="561" y="86" text-anchor="middle" class="reading-svg-label" font-size="11">dedicated to</text><text x="561" y="101" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#806b2a">research</text></g>
      <g><rect x="684" y="66" width="124" height="58" rx="3" fill="#1a52e0" stroke="#1a52e0"/><text x="746" y="89" text-anchor="middle" class="reading-svg-label" font-size="12" font-weight="700" fill="#fff">highly</text><text x="746" y="105" text-anchor="middle" class="reading-svg-label" font-size="12" font-weight="700" fill="#fff">dedicated</text><text x="746" y="118" text-anchor="middle" class="reading-svg-mono" font-size="9" fill="#d9e5ff">to research</text></g>
      <text x="39" y="29" class="reading-svg-mono" font-size="10" fill="#666">CONCRETE EVENTS</text><text x="617" y="29" class="reading-svg-mono" font-size="10" fill="#1a52e0">HIGHER-LEVEL SELF-MODEL</text>
    </svg>
  </div>
  <p class="reading-caption">Events → patterns → a usable story about the self. Because reflections are stored as memories, the tree can keep growing upward.</p>
</section>'''


def render_reading_planning() -> str:
    return '''<section class="reading-subsection" aria-labelledby="reading-planning-title">
  <div class="reading-subhead"><span class="reading-index">04</span><div><h2 id="reading-planning-title">Planning gives time a shape.</h2><p>The agent starts broad, decomposes the next hours into smaller actions, and regenerates the plan when an important observation interrupts the day.</p></div></div>
  <div class="reading-plan">
    <div class="reading-plan-axis"><span></span><span>7a</span><span>9a</span><span>11a</span><span>1p</span><span>3p</span><span>5p</span><span>7p</span><span>9p</span></div>
    <div class="reading-plan-row"><strong>broad agenda</strong><div class="reading-plan-track"><i class="teal" style="grid-column:1 / span 2">morning routine</i><i class="teal" style="grid-column:3 / span 3">classes / research</i><i class="warm" style="grid-column:6 / span 2">lunch + walk</i><i class="teal" style="grid-column:8 / span 3">write composition</i><i class="quiet" style="grid-column:11 / span 2">dinner / sleep</i></div></div>
    <div class="reading-plan-row"><strong>near future</strong><div class="reading-plan-track"><i class="teal" style="grid-column:8 / span 1">brainstorm</i><i class="teal" style="grid-column:9 / span 1">draft</i><i class="warm" style="grid-column:10 / span 1">break</i><i class="teal" style="grid-column:11 / span 1">polish</i></div></div>
    <div class="reading-plan-row"><strong>moment to moment</strong><div class="reading-plan-track"><i class="quiet" style="grid-column:8 / span 1">snack</i><i class="quiet" style="grid-column:9 / span 1">walk</i><i class="warm" style="grid-column:10 / span 1">reset</i><i class="quiet" style="grid-column:11 / span 1">clean desk</i></div></div>
  </div>
  <p class="reading-replan"><span aria-hidden="true">↳</span><span><strong>Unexpected observation:</strong> John sees Eddy walking. John retrieves what he knows about Eddy, decides a conversation is appropriate, generates dialogue, and rebuilds the plan from that moment.</span></p>
</section>'''


def render_reading_society() -> str:
    return '''<section class="reading-subsection" aria-labelledby="reading-society-title">
  <div class="reading-subhead"><span class="reading-index">05</span><div><h2 id="reading-society-title">Then one intention becomes a cascade.</h2><p>Isabella’s party is the paper’s compact demonstration of group behavior: information spreads, ties form, preparations happen, and attendance remains imperfect.</p></div></div>
  <div class="reading-society-grid">
    <div class="reading-diagram reading-network-diagram">
      <svg class="reading-svg" viewBox="0 0 760 310" role="img" aria-labelledby="society-svg-title society-svg-desc">
        <title id="society-svg-title">Party information diffusion</title>
        <desc id="society-svg-desc">Isabella is the central origin of a party invitation that reaches twelve other named agents through direct and indirect conversations.</desc>
        <defs><marker id="reading-network-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#8fa1ab"/></marker></defs>
        <g class="reading-network-edges" fill="none" stroke="#aab8b4" stroke-width="1.6" stroke-dasharray="5 6" marker-end="url(#reading-network-arrow)"><path d="M 362 157 C 278 116 222 87 151 65"/><path d="M 362 157 C 327 94 301 64 270 43"/><path d="M 372 157 C 412 93 439 62 472 45"/><path d="M 377 163 C 470 128 531 105 596 95"/><path d="M 380 171 C 482 171 551 169 623 170"/><path d="M 374 176 C 435 224 493 248 555 258"/><path d="M 361 184 C 350 233 333 263 302 284"/><path d="M 151 83 C 161 150 177 218 188 248"/><path d="M 349 163 C 279 157 218 169 153 186"/><path d="M 350 154 C 279 102 220 56 170 32"/><path d="M 472 63 C 477 139 480 216 486 270"/><path d="M 384 174 C 490 205 571 222 670 224"/></g>
        <g class="reading-network-node"><circle cx="366" cy="169" r="32" fill="#1a52e0"/><text x="366" y="166" text-anchor="middle" fill="#fff" font-size="12" font-weight="700">Isabella</text><text x="366" y="181" text-anchor="middle" fill="#d9e5ff" font-size="9">origin</text></g>
        <g class="reading-network-node"><circle cx="151" cy="65" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="151" y="96" text-anchor="middle" font-size="10">Sam</text></g><g class="reading-network-node"><circle cx="270" cy="43" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="270" y="21" text-anchor="middle" font-size="10">Maria</text></g><g class="reading-network-node"><circle cx="472" cy="45" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="472" y="21" text-anchor="middle" font-size="10">Klaus</text></g><g class="reading-network-node"><circle cx="596" cy="95" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="596" y="125" text-anchor="middle" font-size="10">John</text></g><g class="reading-network-node"><circle cx="623" cy="170" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="623" y="201" text-anchor="middle" font-size="10">Tom</text></g><g class="reading-network-node"><circle cx="555" cy="258" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="555" y="289" text-anchor="middle" font-size="10">Ayesha</text></g><g class="reading-network-node"><circle cx="302" cy="284" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="302" y="309" text-anchor="middle" font-size="10">Eddy</text></g><g class="reading-network-node"><circle cx="188" cy="266" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="188" y="296" text-anchor="middle" font-size="10">Jennifer</text></g><g class="reading-network-node"><circle cx="153" cy="186" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="153" y="216" text-anchor="middle" font-size="10">Giorgio</text></g><g class="reading-network-node"><circle cx="170" cy="32" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="170" y="10" text-anchor="middle" font-size="10">Latoya</text></g><g class="reading-network-node"><circle cx="486" cy="288" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="486" y="309" text-anchor="middle" font-size="10">Abigail</text></g><g class="reading-network-node"><circle cx="670" cy="224" r="18" fill="#f5f7ff" stroke="#1a52e0"/><text x="670" y="255" text-anchor="middle" font-size="10">Wolfgang</text></g>
      </svg>
    </div>
    <div class="reading-society-copy"><p class="reading-caption reading-society-caption">Arrows show a simplified mix of direct invitations and second-hop conversations.</p><div class="reading-society-metrics"><div><b>1 → 13</b><span>knew about the party</span></div><div><b>5 / 12</b><span>invitees showed up</span></div><div><b>0.167 → 0.74</b><span>network density</span></div><div><b>1 → 8</b><span>knew Sam’s candidacy</span></div></div><div class="reading-callout"><strong>Awareness is not coordination.</strong><p>The information moved farther than the people did. Some had conflicts; others were interested but never turned interest into a plan.</p></div></div>
  </div>
</section>'''


def render_reading_evidence() -> str:
    return '''<section class="reading-subsection" aria-labelledby="reading-evidence-title">
  <div class="reading-subhead"><span class="reading-index">07</span><div><h2 id="reading-evidence-title">The result—and the boundary.</h2><p>When evaluators ranked five versions of the agent, the full architecture came out on top. That supports the value of the scaffold in this setting, not a claim of general intelligence.</p></div></div>
  <div class="reading-evidence-grid"><div class="reading-evidence-bars"><div class="reading-evidence-row"><span>full architecture</span><i style="width:99.6%"></i><b>29.89</b></div><div class="reading-evidence-row"><span>no reflection</span><i style="width:89.6%"></i><b>26.88</b></div><div class="reading-evidence-row"><span>no reflection + planning</span><i style="width:85.5%"></i><b>25.64</b></div><div class="reading-evidence-row muted"><span>human crowdworker</span><i style="width:76.5%"></i><b>22.95</b></div><div class="reading-evidence-row muted"><span>no memory / plan / reflection</span><i style="width:70.7%"></i><b>21.21</b></div></div><div class="reading-boundary"><p class="reading-label">READ IT CRITICALLY</p><p><strong>Believable</strong> means the behavior reads as plausible to evaluators.</p><p><strong>Emergent</strong> means the event was not scripted step by step.</p><p><strong>Neither</strong> establishes consciousness, human-level understanding, or robust long-term autonomy.</p></div></div>
</section>'''


def render_reading_detail(item: dict) -> str:
    short_title = item.get("short_title", item["title"])
    subtitle = item.get("subtitle", "")
    story = item["story"]
    sections = "".join(
        f'<section class="reading-text-section"><h2>{e(section["title"])}</h2><p>{e(section["body"])}</p></section>'
        for section in item["sections"]
    )
    tags = " · ".join(e(tag) for tag in item["tags"])
    return "".join([
        plain_open(f"{item['title']} — Sumant", item["summary"], f"/reading/{item['slug']}/", body_class="notes-page reading-page reading-detail-page"),
        '<main id="main" tabindex="-1"><article class="reading-entry">',
        f'''<header class="detail-header reading-entry-header">
  <a class="breadcrumb" href="/reading/">← reading / {e(item['order'])}</a>
  <p class="detail-meta">{e(item['status'].lower())} · {e(item['period'])} · {e(item['venue'])}</p>
  <h1>{e(short_title)}</h1>
  <p class="reading-paper-title">{e(subtitle)} · {e(item['venue'])}</p>
  <p class="reading-story-hook">{e(story['headline'])}</p>
  <p class="detail-lead">{e(story['intro'])}</p>
</header>
<dl class="meta-list reading-meta-list">
  <div><dt>authors</dt><dd>{e(item['authors'])}</dd></div>
  <div><dt>fields</dt><dd>{tags}</dd></div>
  <div><dt>paper</dt><dd><a href="{e(item['source_url'])}" rel="noopener">DOI / published paper ↗</a></dd></div>
</dl>
<div class="reading-body">
{render_reading_orientation(item)}
{render_reading_story(item)}
{render_reading_principles(item)}
{render_reading_loop()}
{render_reading_retrieval()}
{render_reading_reflection()}
{render_reading_planning()}
{render_reading_society()}
{render_reading_build(item)}
{render_reading_evidence()}
{sections}
</div>
<p class="detail-links reading-detail-links"><a href="{e(item['source_url'])}" rel="noopener">Read the paper ↗</a></p>
<p class="next-work"><span>reading list:</span><br><a class="live" href="/reading/">← all papers</a></p>''',
        '</article></main>', footer(), '<script src="/scripts/site.js"></script></body></html>\n',
    ])


def render_feed() -> str:
    entries = []
    for item in DATA["updates"]:
        url = absolute(f"/work/{item['work_slug']}/")
        entries.append(f"""  <entry>
    <title>{xml_escape(item['title'])}</title>
    <id>{xml_escape(url)}#{xml_escape(item['date'])}</id>
    <link href="{xml_escape(url)}"/>
    <updated>{xml_escape(item['date'])}T00:00:00Z</updated>
    <summary>{xml_escape(item['body'])}</summary>
  </entry>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Sumant — recent work</title>
  <id>{xml_escape(SITE['url'])}/</id>
  <link href="{xml_escape(SITE['url'])}/feed.xml" rel="self"/>
  <link href="{xml_escape(SITE['url'])}/"/>
  <updated>{xml_escape(SITE['updated'])}T00:00:00Z</updated>
  <author><name>Sumant</name></author>
{chr(10).join(entries)}
</feed>
"""


def write(relative: str, value: str) -> None:
    path = (ROOT / relative).resolve()
    if path == ROOT or ROOT not in path.parents:
        raise ValueError(f"refusing to write outside site root: {relative!r}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    print(f"built {path.relative_to(ROOT)}")


def validate_data() -> None:
    if not WORK:
        raise ValueError("content must include at least one work record")
    slugs = [item["slug"] for item in WORK]
    invalid = [slug for slug in slugs if not SAFE_SLUG.fullmatch(slug)]
    if invalid:
        raise ValueError(f"unsafe work slug(s): {invalid}")
    if len(slugs) != len(set(slugs)):
        raise ValueError("work slugs must be unique")
    references = [DATA["now"]["work_slug"]]
    references.extend(item["work_slug"] for item in DATA["updates"])
    missing = sorted(set(references) - set(slugs))
    if missing:
        raise ValueError(f"unknown work reference(s): {missing}")
    for item in WORK:
        cover = item.get("cover")
        if cover and cover["src"].startswith("/"):
            asset = (ROOT / cover["src"].lstrip("/")).resolve()
            if ROOT not in asset.parents or not asset.is_file():
                raise ValueError(f"missing or unsafe cover asset: {cover['src']!r}")
    reading_slugs = [item["slug"] for item in READING]
    invalid_reading = [slug for slug in reading_slugs if not SAFE_SLUG.fullmatch(slug)]
    if invalid_reading:
        raise ValueError(f"unsafe reading slug(s): {invalid_reading}")
    if len(reading_slugs) != len(set(reading_slugs)):
        raise ValueError("reading slugs must be unique")


def main() -> None:
    validate_data()
    write("index.html", render_home())
    write("work/index.html", render_archive())
    for index, item in enumerate(WORK):
        write(f"work/{item['slug']}/index.html", render_detail(item, WORK[(index + 1) % len(WORK)]))
    write("reading/index.html", render_reading_archive())
    for item in READING:
        # A "handwritten" entry keeps its own reading/<slug>/index.html on disk and
        # only takes its row in the archive from here. render_reading_detail() renders
        # the paper-note layout and would overwrite a hand-built page.
        if item.get("handwritten"):
            continue
        write(f"reading/{item['slug']}/index.html", render_reading_detail(item))
    write("feed.xml", render_feed())


if __name__ == "__main__":
    main()
