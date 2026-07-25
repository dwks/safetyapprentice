#!/usr/bin/env python3
"""Render the site from templates/ into a static output directory.

    python3 build.py              # -> dist/
    python3 build.py --out public
    python3 build.py --serve      # build, then serve dist/ on :8000

Everything in the output directory is generated; point a web server at it.
Nav and footer live in templates/_nav.html and templates/_footer.html, and
their contents come from site.py — change them in one place.
"""
import argparse
import http.server
import functools
import shutil
import socketserver
import sys
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
except ModuleNotFoundError:
    sys.exit(
        "jinja2 is not installed.\n"
        "  python3 -m venv .venv && .venv/bin/pip install jinja2\n"
        "then run:  .venv/bin/python build.py"
    )

from siteconf import ASSETS, PAGES, SITE   # noqa: E402  (local module)

ROOT = Path(__file__).parent.resolve()


def build(out_dir: Path) -> int:
    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    out_dir.mkdir(parents=True, exist_ok=True)

    # Wipe only what we generate, so a stray output dir isn't destructive.
    for stale in out_dir.glob("*.html"):
        stale.unlink()

    for page in PAGES:
        page = {"content_width": 720, "group": None, "description": None, **page}
        template = env.get_template(f"pages/{page['slug']}.html")
        html = template.render(page=page, site=SITE)
        (out_dir / f"{page['slug']}.html").write_text(html, encoding="utf-8")
        print(f"  {page['slug']}.html")

    for name in ["style.css", "site.js", *ASSETS]:
        src = ROOT / "static" / name
        if not src.exists():
            src = ROOT / name
        if not src.exists():
            print(f"  ! missing asset: {name}")
            continue
        shutil.copy2(src, out_dir / name)
        print(f"  {name}")

    return len(PAGES)


def serve(out_dir: Path, port: int = 8000) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(out_dir))
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\nserving {out_dir} at http://localhost:{port}  (ctrl-c to stop)")
        httpd.serve_forever()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="dist", help="output directory (default: dist)")
    ap.add_argument("--serve", action="store_true", help="serve the output after building")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    out_dir = (ROOT / args.out).resolve()
    print(f"building into {out_dir}")
    n = build(out_dir)
    print(f"\n{n} pages built.")

    if args.serve:
        serve(out_dir, args.port)


if __name__ == "__main__":
    main()
