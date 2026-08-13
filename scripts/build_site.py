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
  <p>Contact:<br>{socials} · <a href="/feed.xml">rss</a></p>
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
        f'<p class="now-line" id="now"><span class="live-dot" aria-hidden="true"></span><a class="live" href="/work/{e(DATA["now"]["work_slug"])}/">now · august 2026</a> — {e(DATA["now"]["title"])}. {e(DATA["work"][0]["summary"])}</p>',
        f'<ul class="project-list" id="work">{featured}</ul>',
        '<p class="small-link"><a class="live" href="/work/">all work →</a></p>',
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


def plain_open(title: str, description: str, path: str) -> str:
    return "".join([
        head(title, description, path),
        '<body class="notes-page"><a class="skip-link" href="#main">Skip to content</a>',
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


def main() -> None:
    validate_data()
    write("index.html", render_home())
    write("work/index.html", render_archive())
    for index, item in enumerate(WORK):
        write(f"work/{item['slug']}/index.html", render_detail(item, WORK[(index + 1) % len(WORK)]))
    write("feed.xml", render_feed())


if __name__ == "__main__":
    main()
