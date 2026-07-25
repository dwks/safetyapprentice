# The Safety Apprentice

A curated, somewhat opinionated guide for people getting into AI safety —
covering why the field matters, how hiring actually works, where the hubs and
conferences are, and what the core concepts and key events have been.

Live at **[safetyapprentice.com](https://safetyapprentice.com)**.

## Building the site

The site is static HTML, generated from Jinja templates so that the nav, footer,
and shared styling only exist in one place.

```bash
python3 -m venv .venv
.venv/bin/pip install jinja2

.venv/bin/python build.py            # -> dist/
.venv/bin/python build.py --serve    # build, then serve on localhost:8000
```

`build.py` renders every page into `dist/` and copies the CSS, JS, and images
alongside it. Point a web server at `dist/` — nothing else is needed at runtime.

Useful flags: `--out <dir>` to build somewhere else, `--port <n>` with `--serve`.

## Layout

| Path | What it is |
| --- | --- |
| `siteconf.py` | Nav structure, footer links, and per-page metadata (title, accent colour, content width). **Add a new page here.** |
| `templates/base.html` | The page skeleton — head, background, nav, hero, content, footer, scripts. |
| `templates/_nav.html`, `_footer.html` | The nav and footer, defined once and shared by every page. |
| `templates/pages/*.html` | One template per page: its own CSS, hero, and content. |
| `static/style.css` | Shared site chrome. Per-page accent colours come from CSS custom properties. |
| `static/site.js` | Navbar scroll state, fade-in reveals, nav dropdowns. |
| `dist/` | Generated output. Not tracked — rebuild it with `build.py`. |

## Adding a page

1. Add an entry to `PAGES` in `siteconf.py` (and to `NAV` if it should be linked).
2. Create `templates/pages/<slug>.html`:

```jinja
{% extends "base.html" %}

{% block page_css %}
  /* rules specific to this page */
{% endblock %}

{% block hero %}
<header class="hero">
  <h1>Page <span>title</span></h1>
  <p class="tagline">One-line summary.</p>
</header>
{% endblock %}

{% block content %}
<section class="content">
  ...
</section>
{% endblock %}
```

3. Rebuild.

Page accents are set from `siteconf.py` and exposed as `--accent`, `--accent-2`,
and `--accent-3`, so hero gradients and dividers pick them up automatically.

## Analytics

Cookieless [Plausible](https://plausible.io) for visitor numbers, plus nginx
access logs aggregated with GoAccess on the server. No cookies, no cross-site
tracking, no consent banner. One field in `siteconf.py` turns Plausible off
again. See [docs/analytics.md](docs/analytics.md).

## Contributing

Corrections and additions are welcome — especially anything that has gone stale.
Open an issue or a pull request. Contributions are accepted under the same
license as the rest of the project.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — share and adapt,
including commercially, with credit. Full text in [LICENSE](LICENSE).

> The Safety Apprentice by David Williams-King —
> https://safetyapprentice.com — CC BY 4.0

This covers the original material here: the writing, and the templates,
stylesheet, and build script that produce it. It does not extend to short
quotations from papers, reports, and statements, which remain with their
authors; nor to the project name, so please rename anything you fork.

The world map is ["World Map" by shokunin](https://openclipart.org/detail/19011/world-map-by-shokunin)
via Openclipart, public domain. DM Sans and Lora are loaded from Google Fonts
under the SIL Open Font License.
