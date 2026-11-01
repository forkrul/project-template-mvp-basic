#!/usr/bin/env python3
"""Assemble cluster markdown fragments into one atlas page.

Each subagent wrote one `cluster-NN-*.md` file using a fixed per-item template.
This converts that markdown to HTML and wraps it in `shell.html`.

Run it from the directory holding the fragments:  python3 build.py
Clusters are discovered by filename and ordered by their NN prefix; each
cluster's title comes from its own H1, and the prose between that H1 and the
first `##` becomes the cluster standfirst.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
OUT = HERE / "atlas.html"

# Masthead and rail copy. Override any key by dropping an atlas.json next to
# this script — always rewrite these for the subject; the defaults are a
# placeholder, not a house style.
DEFAULT_COPY = {
    "TITLE": "Atlas",
    "BRAND_KICKER": "Atlas",
    "BRAND_TITLE": "corpus<br />atlas",
    "EYEBROW": "Corpus survey",
    "HEADLINE": "What was specified, and what actually exists",
    "STANDFIRST": (
        "Every item in the corpus, read end to end: what it is for, how it "
        "behaves, the API surface behind it, and — the part the documents "
        "never say — whether any of it is real."
    ),
    # Set this to the ref you verified against. An atlas without a stated ref
    # is undated evidence: a working tree hundreds of commits behind trunk
    # reports shipped features as "spec only" and reads exactly as confidently.
    "PROVENANCE": "",
    # FR-021: a plain href string (e.g. "api/api.html") or "" for no link.
    # main() turns it into the whole <a> element; an empty value renders nothing.
    "API_LINK": "",
}


def discover() -> list[pathlib.Path]:
    """Fragments in NN order. Filenames are `cluster-NN-<slug>.md`."""
    found = sorted(
        [*HERE.glob("cluster-*.md"), *(HERE / "clusters").glob("cluster-*.md")],
        key=lambda p: (
            int(m.group(1)) if (m := re.match(r"cluster-(\d+)", p.name)) else 999,
            p.name,
        ),
    )
    if not found:
        raise SystemExit(f"no cluster-*.md fragments found in {HERE}")
    return found

STATUS_SLUGS = {
    "shipped": "shipped",
    "live": "shipped",
    "backend only": "backend",
    "partial": "partial",
    "spec only": "spec",
}

GHERKIN_KW = re.compile(
    r"^(\s*)"
    r"(Feature|Scenario Outline|Scenario|Background"
    r"|Given|When|Then|And|But|Examples):?",
)
GHERKIN_STRUCT = ("Feature", "Scenario", "Scenario Outline", "Background", "Examples")

# Separators between an id and its title: em dash, en dash, hyphen. Written as
# escapes because the en dash looks like a hyphen (ruff RUF001).
DASHES = "\u2014\u2013-"


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def inline(s: str) -> str:
    """Inline markdown: code, bold, italic, links.

    Code spans are pulled out first so their contents are never treated as
    markup, but emphasis is matched across the gaps they leave — otherwise
    bold wrapping a code span (**there is no `/renewal` route**) never closes.
    """
    spans: list[str] = []

    def stash(m: re.Match[str]) -> str:
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    s = re.sub(r"`([^`]+)`", stash, s)
    s = _inline_no_code(s)
    return re.sub(
        r"\x00(\d+)\x00",
        lambda m: f"<code>{esc(spans[int(m.group(1))])}</code>",
        s,
    )


def _inline_no_code(s: str) -> str:
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    # Lazy, so bold survives an italic nested inside it (**a *b* c**).
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    return s


def gherkin(block: str) -> str:
    lines = []
    for raw in block.split("\n"):
        m = GHERKIN_KW.match(raw)
        if m:
            kw = m.group(2)
            rest = raw[m.end() :]
            cls = "g-struct" if kw in GHERKIN_STRUCT else "g-step"
            sep = ":" if raw[m.end(2) : m.end(2) + 1] == ":" else ""
            lines.append(
                f'{m.group(1)}<span class="{cls}">{esc(kw)}{sep}</span>{esc(rest)}'
            )
        else:
            lines.append(esc(raw))
    return '<pre class="gherkin"><code>' + "\n".join(lines) + "</code></pre>"


def split_status(text: str) -> tuple[str, str, str]:
    """Split a status field into (slug, pill label, trailing qualifier).

    Agents wrote values like "Partial (backend built, routers never mounted)",
    so the pill takes the leading status word and the rest becomes a note —
    otherwise a whole sentence lands inside the pill and misses the slug.
    """
    t = text.strip()
    low = t.lower()
    for phrase in sorted(STATUS_SLUGS, key=len, reverse=True):
        if low.startswith(phrase):
            rest = t[len(phrase) :].lstrip(" ,;:" + DASHES)
            label = t[: len(phrase)]
            return STATUS_SLUGS[phrase], label, rest
    return "spec", t.split("(")[0].strip() or t, ""


def status_pill(text: str) -> str:
    slug, label, rest = split_status(text)
    pill = f'<span class="pill pill--{slug}">{esc(label)}</span>'
    if rest:
        pill += f'<span class="meta-note">{inline(rest)}</span>'
    return pill


def render_meta(line: str) -> str:
    """The '**Status:** X · **Persona:** Y · **Supersedes:** Z' line."""
    parts = [p.strip() for p in re.split(r"\s*·\s*", line) if p.strip()]
    chunks = []
    for p in parts:
        m = re.match(r"\*\*([^:*]+):?\*\*\s*(.*)", p)
        if not m:
            chunks.append(f'<span class="meta-item">{inline(p)}</span>')
            continue
        key, val = m.group(1).strip(), m.group(2).strip()
        if key.lower() == "status":
            chunks.append(
                '<span class="meta-item"><span class="meta-k">Status</span>'
                f"{status_pill(val)}</span>"
            )
        else:
            chunks.append(
                f'<span class="meta-item"><span class="meta-k">{esc(key)}</span>'
                f'<span class="meta-v">{inline(val)}</span></span>'
            )
    return f'<div class="meta">{"".join(chunks)}</div>'


def table(rows: list[str]) -> str:
    cells = [
        [c.strip() for c in re.sub(r"^\||\|$", "", r).split("|")] for r in rows
    ]
    if len(cells) >= 2 and all(re.fullmatch(r":?-{2,}:?", c) for c in cells[1] if c):
        head, body = cells[0], cells[2:]
    else:
        head, body = cells[0], cells[1:]
    out = ['<div class="table-wrap"><table><thead><tr>']
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>")
        for i, c in enumerate(r):
            cls = ""
            low = c.strip().lower()
            if low in ("live", "proposed"):
                cls = f' class="state state--{low}"'
            elif i == 0 and c.strip().upper() in (
                "GET", "POST", "PUT", "PATCH", "DELETE",
            ):
                cls = f' class="verb verb--{c.strip().lower()}"'
            out.append(f"<td{cls}>{inline(c)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def starts_block(line: str) -> bool:
    """True if the line opens a construct that must not be swallowed into a
    running paragraph. Used to decide where a paragraph ends."""
    s = line.strip()
    if not s:
        return True
    return bool(
        s.startswith("```")
        or (s.startswith("|") and s.endswith("|"))
        or re.match(r"^#{1,4}\s+", s)
        or re.match(r"^(-{3,}|\*{3,}|_{3,})$", s)
        or re.match(r"^(\s*)([-*+]|\d+\.)\s+", line)
        or s.startswith("**Status:**")
        or s.startswith(">")
    )


def convert(md: str, cid: str) -> tuple[str, list[dict]]:
    """Markdown → HTML for one cluster. Returns (html, feature index)."""
    lines = md.split("\n")
    out: list[str] = []
    feats: list[dict] = []
    i = 0
    open_feature = False
    list_stack: list[str] = []

    def close_lists() -> None:
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    while i < len(lines):
        line = lines[i]

        # fenced code
        if line.strip().startswith("```"):
            lang = line.strip().strip("`").strip()
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            close_lists()
            body = "\n".join(buf)
            if lang.lower() in ("gherkin", "cucumber", "feature"):
                out.append(gherkin(body))
            else:
                out.append(f"<pre><code>{esc(body)}</code></pre>")
            i = j + 1
            continue

        # tables
        if line.strip().startswith("|") and line.strip().endswith("|"):
            j = i
            rows = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(lines[j].strip())
                j += 1
            close_lists()
            out.append(table(rows))
            i = j
            continue

        stripped = line.strip()

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)", stripped)
        if m:
            close_lists()
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1:
                i += 1
                continue  # cluster title comes from the shell
            if level == 2:
                if open_feature:
                    out.append("</section>")
                fm = re.match(
                    r"^([0-9]{3}[a-z0-9-]*|ux2-[0-9]+)\s*[\u2014\u2013-]\s*(.*)",
                    text,
                )
                fid = f"{cid}-f{len(feats)}"
                if fm:
                    slug, title = fm.group(1), fm.group(2)
                    feats.append({"id": fid, "slug": slug, "title": title})
                    out.append(f'<section class="feature" id="{fid}" data-status="">')
                    out.append(
                        f'<h3 class="feature-h"><span class="fid">{esc(slug)}</span>'
                        f"<span class=\"ftitle\">{inline(title)}</span></h3>"
                    )
                else:
                    feats.append({"id": fid, "slug": "", "title": text})
                    out.append(
                        '<section class="feature feature--plain"'
                        f' id="{fid}" data-status="">'
                    )
                    out.append(
                        '<h3 class="feature-h"><span class="ftitle">'
                        f"{inline(text)}</span></h3>"
                    )
                open_feature = True
            else:
                out.append(f"<h{level+1} class=\"sub\">{inline(text)}</h{level+1}>")
            i += 1
            continue

        # horizontal rule = feature separator
        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped):
            close_lists()
            i += 1
            continue

        # lists
        lm = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)", line)
        if lm:
            indent, marker, text = len(lm.group(1)), lm.group(2), lm.group(3)
            want = "ol" if marker.endswith(".") else "ul"
            depth = indent // 2
            while len(list_stack) > depth + 1:
                out.append(f"</{list_stack.pop()}>")
            if not list_stack or len(list_stack) < depth + 1:
                out.append(f"<{want}>")
                list_stack.append(want)
            out.append(f"<li>{inline(text)}</li>")
            i += 1
            continue

        if not stripped:
            close_lists()
            i += 1
            continue

        # the meta line
        if stripped.startswith("**Status:**"):
            close_lists()
            out.append(render_meta(stripped))
            sm = re.search(r"\*\*Status:?\*\*\s*([^·|]+)", stripped)
            if sm and feats:
                st = split_status(sm.group(1))[0]
                for k in range(len(out) - 1, -1, -1):
                    if 'class="feature' in out[k] and 'data-status=""' in out[k]:
                        out[k] = out[k].replace('data-status=""', f'data-status="{st}"')
                        feats[-1]["status"] = st
                        break
            i += 1
            continue

        # blockquote — consecutive '>' lines become one <blockquote>
        if stripped.startswith(">"):
            close_lists()
            buf = []
            j = i
            while j < len(lines) and lines[j].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[j]))
                j += 1
            body = " ".join(x.strip() for x in buf if x.strip())
            qm = re.match(r"^\*\*([^*]+)\*\*\s*(.*)", body)
            if qm and len(qm.group(1)) < 60:
                inner = (
                    f'<p class="labelled"><span class="label">'
                    f'{esc(qm.group(1).rstrip(".:"))}</span>{inline(qm.group(2))}</p>'
                )
            else:
                inner = f"<p>{inline(body)}</p>"
            out.append(f"<blockquote>{inner}</blockquote>")
            i = j
            continue

        # Paragraph: join wrapped lines before any inline conversion. Without
        # this each source line becomes its own <p>, which shreds wrapped prose
        # and makes bold spanning a line break impossible to close — the
        # `**...`code`...**` bug is only half-fixed by inline() if the emphasis
        # never sees both delimiters in one string.
        j = i + 1
        para = [stripped]
        while j < len(lines) and not starts_block(lines[j]):
            para.append(lines[j].strip())
            j += 1
        text = " ".join(para)

        # labelled paragraph e.g. **Design handover notes.** ...
        pm = re.match(r"^\*\*([^*]+)\*\*\s*(.*)", text, re.S)
        if pm and len(pm.group(1)) < 60:
            close_lists()
            label = pm.group(1).rstrip(".:")
            rest = pm.group(2)
            out.append(
                f'<p class="labelled"><span class="label">{esc(label)}</span>'
                f"{inline(rest)}</p>"
            )
            i = j
            continue

        close_lists()
        out.append(f"<p>{inline(text)}</p>")
        i = j

    close_lists()
    if open_feature:
        out.append("</section>")
    return "".join(out), feats


def main() -> None:
    body_parts = []
    nav_parts = []
    counts = {"shipped": 0, "backend": 0, "partial": 0, "spec": 0}
    total = 0

    for idx, p in enumerate(discover(), start=1):
        raw = p.read_text()
        label = p.stem
        cid = f"c{idx:02d}"
        # cluster overview = the prose between the H1 and the first H2
        m1 = re.search(r"^#\s+(.*)$", raw, re.M)
        title = m1.group(1).strip() if m1 else label
        title = re.sub(r"^Cluster\s+\d+\s*[\u2014\u2013-]\s*", "", title)
        intro = ""
        if m1:
            after = raw[m1.end() :]
            stop = re.search(r"^##\s", after, re.M)
            intro_md = after[: stop.start()] if stop else after
            intro = " ".join(
                x.strip() for x in intro_md.strip().split("\n") if x.strip()
            )

        chtml, feats = convert(raw, cid)
        for f in feats:
            st = f.get("status", "spec")
            counts[st] = counts.get(st, 0) + 1
            total += 1

        body_parts.append(
            f'<section class="cluster" id="{cid}">'
            f'<header class="cluster-h">'
            f'<span class="cluster-n">{idx:02d}</span>'
            f"<h2>{esc(title)}</h2>"
            f'<p class="cluster-intro">{inline(intro)}</p>'
            f"</header>{chtml}</section>"
        )
        links = "".join(
            f'<a href="#{f["id"]}" class="navf" data-status="{f.get("status","spec")}">'
            f'<span class="navf-id">{esc(f["slug"])}</span>'
            f'<span class="navf-t">{esc(f["title"])}</span></a>'
            for f in feats
            if f["slug"]
        )
        nav_parts.append(
            f'<div class="nav-cluster"><a class="nav-c" href="#{cid}">'
            f'<span class="nav-n">{idx:02d}</span>{esc(title)}</a>'
            f'<div class="nav-feats">{links}</div></div>'
        )

    copy = dict(DEFAULT_COPY)
    cfg = HERE / "atlas.json"
    if cfg.exists():
        copy.update(json.loads(cfg.read_text()))

    shell = (HERE / "shell.html").read_text()
    subs = {
        "<!--NAV-->": "".join(nav_parts),
        "<!--BODY-->": "".join(body_parts),
        "{{TOTAL}}": str(total),
        "{{SHIPPED}}": str(counts["shipped"]),
        "{{BACKEND}}": str(counts["backend"]),
        "{{PARTIAL}}": str(counts["partial"]),
        "{{SPEC}}": str(counts["spec"]),
    }
    subs.update({"{{" + k + "}}": v for k, v in copy.items()})
    href = str(copy.get("API_LINK") or "").strip()
    subs["<!--API_LINK-->"] = (
        f'<p class="apilink"><a href="{html.escape(href, quote=True)}">'
        "API reference &rarr;</a></p>" if href else ""
    )
    page = shell
    for k, v in subs.items():
        page = page.replace(k, v)

    # An OPEN comment pattern, not an allow-list: every declared slot has an
    # unconditional subs entry, so listing them could never match. The real
    # failure is a slot in shell.html with no subs entry at all.
    left = re.findall(r"\{\{[A-Z_]+\}\}|<!--[A-Z_]+-->", page)
    if left:
        raise SystemExit(f"unsubstituted slots: {sorted(set(left))}")

    if not copy.get("PROVENANCE"):
        sys.stdout.write(
            "WARNING no PROVENANCE set — the page does not say which ref its "
            "statuses were verified against. Set it in atlas.json before "
            "publishing (see SKILL.md step 2).\n"
        )
    OUT.write_text(page)
    sys.stdout.write(f"wrote {OUT} — {total} features, {len(page):,} bytes\n")
    sys.stdout.write(f"counts: {counts}\n")
    write_atlas_md(discover())


def write_atlas_md(frags: list[pathlib.Path]) -> None:
    """Regenerate atlas.md — every fragment concatenated, for one-pass reading.

    This lives here because nothing else regenerated it: the skill's own file
    layout lists atlas.md, so it looked maintained while silently drifting
    behind the fragments beside it. A stale all-in-one file is worse than none,
    because it reads as authoritative.

    Fragment H1s are inconsistent across atlases — some already carry
    "Cluster N — ", some are a bare title — so the prefix is added only when it
    is absent. Adding it unconditionally yields "Cluster 1 — Cluster 1 — …".
    """
    parts = [
        "# Feature atlas — all clusters\n",
        "\nGenerated by `build.py` from `clusters/*.md`. See `README.md` for how\n"
        "statuses were verified and what they mean.\n",
    ]
    for f in frags:
        m = re.match(r"cluster-(\d+)", f.name)
        n = int(m.group(1)) if m else 0
        body = f.read_text().rstrip("\n")
        first, _, rest = body.partition("\n")
        title = first.lstrip("#").strip()
        if not title.lower().startswith("cluster "):
            title = f"Cluster {n} — {title}"
        parts.append(f"\n---\n\n# {title}\n{rest}\n")
    md = "".join(parts)
    (HERE / "atlas.md").write_text(md)
    sys.stdout.write(
        f"wrote {HERE / 'atlas.md'} — {len(frags)} clusters, {len(md):,} bytes\n"
    )


if __name__ == "__main__":
    main()
