"""Site-wide configuration: nav structure, footer, and per-page metadata.

This is the single source of truth for the nav and footer. Adding a page means
adding an entry to PAGES and (if it should be linked) to NAV.
"""

SITE = {
    "name": "The Safety Apprentice",
    "repo": "https://github.com/dwks/safetyapprentice",
    # Mentoring is paused; links go to the in-site "coming soon" page rather
    # than dwkmentoring.com. Point this back at the external site to resume.
    "consulting": "mentoring.html",
    "footer_note": "The Safety Apprentice is a community resource started by David Williams-King.",

    # Plausible analytics. None disables it entirely — no script is emitted.
    # The URL is the per-site one from the Plausible dashboard's installation
    # snippet. See docs/analytics.md.
    "plausible_src": "https://plausible.io/js/pa-Q5aKLIVH4QPBBvMT5qFm3.js",
}

SITE["nav"] = [
    {"label": "Home", "href": "/"},
    {"label": "Learn", "children": [
        {"label": "Why AI Safety Matters", "href": "why-ai-safety.html"},
        {"label": "Choosing Research Problems", "href": "choosing-research-problems.html"},
        {"label": "Research Ideas",        "href": "research-ideas.html"},
        {"label": "Key Events",            "href": "timeline.html"},
        {"label": "Concept Map",           "href": "concept-map.html"},
    ]},
    {"label": "Getting In", "children": [
        {"label": "Getting Hired",     "href": "hard-to-get-hired.html"},
        {"label": "Fellowships",       "href": "fellowships.html"},
        {"label": "Funding &amp; Grants", "href": "funding.html"},
        {"label": "Job Listings",      "href": "jobs.html"},
    ]},
    {"label": "Community", "children": [
        {"label": "Geography",              "href": "geography.html"},
        {"label": "Conferences &amp; Events", "href": "conferences.html"},
    ]},
    {"label": "Mentoring", "href": SITE["consulting"]},
    {"label": "About", "href": "about.html"},
]

SITE["footer_links"] = [
    {"label": "About this project",   "href": "about.html"},
    {"label": "Contribute on GitHub", "href": SITE["repo"],       "external": True},
    {"label": "Mentoring", "href": SITE["consulting"]},
]

# Accent palettes, keyed for reuse across pages.
TERRACOTTA = ["#B85C38", "#C2793D", "#A45B5B"]
ROSE       = ["#C4687A", "#D98E9C", "#B85C38"]
BRONZE     = ["#A0784C", "#C49A6C", "#8B6B3D"]
AMBER      = ["#C2793D", "#E09B5F", "#A0784C"]
OLIVE      = ["#8B7040", "#B09358", "#7A6235"]
PINE       = ["#4A7C6F", "#6FA294", "#3B82A0"]

# `group` marks which nav dropdown should show as active.
PAGES = [
    {"slug": "index",              "title": None,                      "accent": TERRACOTTA, "content_width": 920},
    {"slug": "why-ai-safety",      "title": "Why AI Safety Matters",   "accent": TERRACOTTA, "content_width": 720, "group": "Learn"},
    {"slug": "choosing-research-problems", "title": "Choosing Research Problems", "accent": TERRACOTTA, "content_width": 760, "group": "Learn"},
    {"slug": "timeline",           "title": "Key Events",              "accent": TERRACOTTA, "content_width": 780, "group": "Learn"},
    {"slug": "concept-map",        "title": "A Concept Map of AI Safety","accent": TERRACOTTA, "content_width": 720, "group": "Learn", "consult": False},
    {"slug": "research-ideas",      "title": "Research Ideas",          "accent": TERRACOTTA, "content_width": 760, "group": "Learn"},
    {"slug": "hard-to-get-hired",  "title": "Why It's Hard to Get Hired", "accent": TERRACOTTA, "content_width": 720, "group": "Getting In"},
    {"slug": "jobs",               "title": "Job Listings",              "accent": PINE,       "content_width": 720, "group": "Getting In"},
    {"slug": "fellowships",        "title": "Fellowships",             "accent": AMBER,      "content_width": 960, "group": "Getting In"},
    {"slug": "funding",            "title": "Funding & Grants",        "accent": OLIVE,      "content_width": 720, "group": "Getting In"},
    {"slug": "geography",          "title": "Geography of AI Safety",  "accent": ROSE,       "content_width": 960, "group": "Community"},
    {"slug": "conferences",        "title": "Conferences & Events",    "accent": BRONZE,     "content_width": 960, "group": "Community"},
    # about already carries its own mentoring panel, so it opts out of the
    # site-wide consulting callout
    {"slug": "mentoring",           "title": "Mentoring",               "accent": TERRACOTTA, "content_width": 720, "consult": False},
    {"slug": "about",              "title": "About",                   "accent": TERRACOTTA, "content_width": 720, "consult": False},
]

# Files copied verbatim into the output directory.
ASSETS = ["neurons.png", "shokunin_World_Map.svg", "world-map.png",
          "favicon.svg", "favicon.png", "favicon.ico", "apple-touch-icon.png",
          "david-williams-king.jpg"]
