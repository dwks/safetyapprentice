# Analytics

Visitor numbers come from nginx's own access logs, aggregated on the server
with [GoAccess](https://goaccess.io). By default the site carries **no
analytics script, no cookies, and no third-party requests** — optional
[Plausible](#plausible) support exists but ships disabled.

That choice is deliberate. This site's audience is unusually likely to run
tracker blockers, so a client-side tool like Google Analytics would undercount
badly and non-randomly. Log analysis can't be blocked, needs no consent banner,
and adds nothing to page weight.

This file documents the server setup. Nothing here affects the built site — it
is all configuration on the VPS.

## How it works

nginx writes every request to `/var/log/nginx/access.log`. Once a day, just
before logrotate rotates that file away, GoAccess folds the day's requests into
a persistent on-disk database and regenerates an HTML dashboard.

Because the aggregation happens *before* rotation, log rotation never costs you
history: the raw lines expire, the totals don't.

```
nginx ──▶ access.log ──▶ [logrotate prerotate] ──▶ GoAccess ──▶ /var/lib/goaccess
                                                        │        (running totals)
                                                        └──────▶ /var/www/stats/index.html
```

## Setup

### 1. GoAccess

```sh
sudo apt install goaccess
goaccess --version          # must be 1.4+ for --persist / --restore
```

If the packaged version is older, use the
[official repo](https://goaccess.io/download#official-repo) — the persistent
database is what makes rotation safe, and it does not exist before 1.4.

### 2. Aggregate before rotation

Debian's packaged nginx logrotate config already runs
`run-parts /etc/logrotate.d/httpd-prerotate` if that directory exists. Using it
avoids editing a packaged conffile, which apt would prompt about on every
upgrade.

```sh
sudo mkdir -p /etc/logrotate.d/httpd-prerotate /var/lib/goaccess /var/www/stats

sudo tee /etc/logrotate.d/httpd-prerotate/goaccess >/dev/null <<'EOF'
#!/bin/sh
exec goaccess /var/log/nginx/access.log \
  --log-format=COMBINED \
  --persist --restore --db-path=/var/lib/goaccess \
  --ignore-crawlers --anonymize-ip \
  -o /var/www/stats/index.html
EOF

sudo chmod +x /etc/logrotate.d/httpd-prerotate/goaccess
```

| Flag | Why |
| --- | --- |
| `--persist` / `--restore` | Write new data to the database, and load the accumulated history first. Together these make totals cumulative. |
| `--db-path` | Where that database lives. Back this up — it *is* your history. |
| `--ignore-crawlers` | Drops known bots. Raw hit counts are heavily inflated without it. |
| `--anonymize-ip` | Stored data is no longer identifying. |
| `--log-format=COMBINED` | nginx's default access log format. Change this if you have customised `log_format`. |

### 3. Keep a safety net

In `/etc/logrotate.d/nginx`, raise `rotate 14` to `rotate 365`. Access logs gzip
roughly 10–20×, so a year is a few megabytes, and it means the database can be
rebuilt from scratch if the aggregation ever breaks:

```sh
zcat /var/log/nginx/access.log.*.gz \
  | goaccess --log-format=COMBINED --persist --db-path=/var/lib/goaccess -o /tmp/rebuild.html
```

### 4. Protect the dashboard

`/var/www/stats` sits outside the site root, and should stay behind auth —
otherwise your traffic stats are public.

```sh
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd dwk     # -c creates; omit it to add more users
sudo chown root:www-data /etc/nginx/.htpasswd
sudo chmod 640 /etc/nginx/.htpasswd
```

> `-c` overwrites the file without warning. Use it once, never again.

Without apache2-utils:

```sh
printf "dwk:$(openssl passwd -apr1)\n" | sudo tee -a /etc/nginx/.htpasswd
```

Then in the server block:

```nginx
location /stats/ {
    auth_basic "stats";
    auth_basic_user_file /etc/nginx/.htpasswd;
    alias /var/www/stats/;
}
```

```sh
sudo nginx -t && sudo systemctl reload nginx
```

### 5. Verify

```sh
sudo logrotate -f /etc/logrotate.d/nginx      # force a cycle
ls -l /var/lib/goaccess /var/www/stats
```

Then load `https://safetyapprentice.com/stats/` and check the date range covers
what you expect.

## Tightening the numbers

The headline "Valid Requests" figure counts *every* HTTP request — each CSS,
JS, and image fetch, plus the constant background of scanner probes any public
VPS attracts. It runs several times higher than the number of people who read a
page. **The figure you actually want is "Unique Visitors".**

To make the panels more honest, keep the options in
`/etc/goaccess/goaccess.conf` rather than growing the prerotate script:

```
log-format COMBINED
ignore-crawlers true
anonymize-ip true

# assets move to their own panel instead of inflating page hits
static-file .css
static-file .js
static-file .svg
static-file .png
static-file .ico
static-file .woff2

# scanner probes (/wp-login.php, /.env, /vendor/...) all 404
ignore-status 404

# your own visits
exclude-ip 203.0.113.7
```

The prerotate script then reduces to:

```sh
#!/bin/sh
exec goaccess /var/log/nginx/access.log \
  --persist --restore --db-path=/var/lib/goaccess \
  -o /var/www/stats/index.html
```

Also check `goaccess --help | grep -i crawler` — recent versions have
`--unknowns-as-crawlers`, which classifies unrecognised user-agents as bots and
catches a good deal that `--ignore-crawlers` misses.

Two caveats:

- **Ignoring 404s hides real broken links too.** Run an occasional report
  without it to check for genuine ones.
- **Filters are not retroactive.** They apply to data folded in from now on; the
  database keeps whatever it already absorbed.

### Rebuilding the database with new filters

Because the archives are kept for a year, the whole history can be reprocessed:

```sh
sudo rm -rf /var/lib/goaccess/*
zcat -f /var/log/nginx/access.log.*.gz \
        /var/log/nginx/access.log.1 \
        /var/log/nginx/access.log \
  | goaccess - --persist --db-path=/var/lib/goaccess -o /var/www/stats/index.html
```

`zcat -f` handles the plain and gzipped files together, and `-` reads stdin.
This only reaches as far back as the oldest archive.

## Is any of this real?

An unadvertised site still gets hundreds of "visitors" and thousands of hits a
day. That is normal, and almost all of it is machines. GoAccess counts a unique
visitor per IP + user-agent per day, and crawlers rotate through both.

The population has changed a lot recently: alongside the old SEO crawlers
(AhrefsBot, SemrushBot, MJ12bot, DataForSeoBot) there is now a large volume of
AI training and retrieval crawlers — GPTBot, ClaudeBot, Bytespider,
Amazonbot, meta-externalagent, PerplexityBot. Many are missing from older
GoAccess browser lists, so `--ignore-crawlers` waves them through.

### Find out what is actually hitting you

```sh
# who, by volume — usually answers the question immediately
awk -F'"' '{print $6}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -25

# a handful of IPs doing hundreds of requests each is a crawler, not readers
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# humans cluster in waking hours; crawlers are flat across 24
awk -F: '{print $2}' /var/log/nginx/access.log | sort | uniq -c
```

### The best proxy for a real visit

Every page loads `style.css` and `site.js`. Crawlers overwhelmingly fetch the
HTML and nothing else — they do not pull subresources. So:

```sh
grep -c 'GET /site\.js' /var/log/nginx/access.log
```

That count is a far better estimate of real page loads than either "visitors"
or "valid requests", and it is hard to fake accidentally. Expect it to be a
small fraction of the headline figure.

Compare it against HTML requests to see the ratio:

```sh
grep -cE 'GET /[a-z-]*\.html|GET / ' /var/log/nginx/access.log
```

If HTML requests vastly exceed `site.js` requests, the gap is bots.

### Cutting the noise at source

Blocking the worst offenders in nginx saves bandwidth as well as tidying the
stats:

```nginx
map $http_user_agent $bad_bot {
    default 0;
    ~*(AhrefsBot|SemrushBot|MJ12bot|DotBot|DataForSeoBot|PetalBot|Bytespider|ImagesiftBot) 1;
}

server {
    if ($bad_bot) { return 403; }
    ...
}
```

Whether to include the AI training crawlers (GPTBot, ClaudeBot, and friends) is
a judgement call rather than a technical one — for a site whose purpose is to
get this material in front of people, having it in training data may be a
feature.

A `robots.txt` handles the polite ones and costs nothing; it is ignored by
exactly the crawlers you most want to stop, so treat it as a supplement to the
block list rather than a replacement.

## Maintenance

- **Glance at the date range monthly.** The failure mode is not rotation — it is
  the prerotate script erroring while logs keep rotating, which loses days
  quietly. If the dashboard's most recent date is stale, that is what happened.
- **Back up `/var/lib/goaccess`.** It holds every total you have. The compressed
  logs are the fallback, but only as far back as `rotate` keeps them.
- **First run is enormous.** GoAccess processes whatever is already in
  `access.log` on its first pass, so the initial figure covers however long that
  file had been accumulating — not one day.
- **Bots still get through.** `--ignore-crawlers` catches known agents; anything
  pretending to be a browser is counted. Treat absolute numbers as generous.

## Known limitations

- Sub-second gap: lines written between the prerotate script finishing and the
  rotation itself are missed. Negligible for traffic counts. For exactness, move
  the same command to `postrotate` against `access.log.1` — safe because
  Debian's config uses `delaycompress`, so `.1` is still plain text.
- No client-side detail — no viewport sizes, no scroll depth, no bounce rate as
  a JS tool would measure it. Pageviews, referrers, paths, user agents, and
  countries are what logs can tell you.
- No live data. The dashboard updates once a day at rotation.

## Plausible

Logs are an *upper* bound: they count every bot that doesn't announce itself.
[Plausible](https://plausible.io) is the natural complement — a ~1KB cookieless
beacon that crawlers never trigger, because they don't run JavaScript. It is a
*lower* bound, since some visitors block it. Real readership is between the two,
and having both numbers is more informative than either alone.

It also removes the manual work: bot filtering becomes Plausible's problem, and
the dashboard reports visitors and pages directly rather than requests.

### Enabling it

Support is already wired in and disabled. In `siteconf.py`:

```python
"plausible": "safetyapprentice.com",     # was None
```

Rebuild, and a single deferred script tag appears in the head of every page.
Set it back to `None` to remove it completely — no leftovers.

Sign up at plausible.io first (from ~€9/month), or
[self-host](https://github.com/plausible/community-edition) it free, in which
case also point `plausible_src` at your own instance.

### Proxying it through this domain

Plausible's default domain is on several blocklists, so a meaningful slice of
this audience would block it. Serving the script and collecting events from
`safetyapprentice.com` avoids that, and makes the request first-party.

Add a proxy to the nginx server block and set:

```python
"plausible_src": "/js/script.js",
```

Plausible documents the nginx configuration —
[follow their proxy guide](https://plausible.io/docs/proxy/introduction) rather
than copying a snippet from here, as the upstream hostnames have changed before.

### If you enable it

The site would no longer be script-free, so the claim at the top of this file
needs revising, and a short privacy line on the about page becomes worth adding.
Plausible sets no cookies and stores no personal data, so it stays a couple of
sentences and no consent banner is required.
