"""Site-wide configuration: nav structure, footer, and per-page metadata.

This is the single source of truth for the nav and footer. Adding a page means
adding an entry to PAGES and (if it should be linked) to NAV.
"""

SITE = {
    "name": "The Safety Apprentice",
    "logo": "\U0001F6E1️",           # 🛡️
    "repo": "https://github.com/dwks/safetyapprentice",
    "consulting": "https://dwkmentoring.com",
    "footer_note": "The Safety Apprentice is a community resource started by David Williams-King.",
}

SITE["nav"] = [
    {"label": "Home", "href": "index.html"},
    {"label": "Learn", "children": [
        {"label": "Why AI Safety Matters", "href": "why-ai-safety.html"},
        {"label": "Key Events",            "href": "timeline.html"},
        {"label": "Field Map",             "href": "concept-map.html"},
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
    {"label": "Mentoring", "href": SITE["consulting"], "external": True},
    {"label": "About", "href": "about.html"},
]

SITE["footer_links"] = [
    {"label": "About this project",   "href": "about.html"},
    {"label": "Contribute on GitHub", "href": SITE["repo"],       "external": True},
    {"label": "Paid career consulting", "href": SITE["consulting"], "external": True},
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
    {"slug": "timeline",           "title": "Key Events",              "accent": TERRACOTTA, "content_width": 780, "group": "Learn"},
    {"slug": "concept-map",        "title": "A Field Map of AI Safety","accent": TERRACOTTA, "content_width": 720, "group": "Learn", "consult": False},
    {"slug": "hard-to-get-hired",  "title": "Why It's Hard to Get Hired", "accent": TERRACOTTA, "content_width": 720, "group": "Getting In"},
    {"slug": "jobs",               "title": "Job Listings",              "accent": PINE,       "content_width": 720, "group": "Getting In"},
    {"slug": "fellowships",        "title": "Fellowships",             "accent": AMBER,      "content_width": 960, "group": "Getting In"},
    {"slug": "funding",            "title": "Funding & Grants",        "accent": OLIVE,      "content_width": 720, "group": "Getting In"},
    {"slug": "geography",          "title": "Geography of AI Safety",  "accent": ROSE,       "content_width": 960, "group": "Community"},
    {"slug": "conferences",        "title": "Conferences & Events",    "accent": BRONZE,     "content_width": 960, "group": "Community"},
    # about already carries the full "A paid career call" panel, so it opts out
    # of the site-wide consulting callout
    {"slug": "about",              "title": "About",                   "accent": TERRACOTTA, "content_width": 720, "consult": False},
]

# Files copied verbatim into the output directory.
ASSETS = ["map3b.png", "map3.png", "shokunin_World_Map.svg"]
