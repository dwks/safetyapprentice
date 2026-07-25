# Analytics

The site carries **no analytics script, no cookies, and no third-party
requests**. Visitor numbers come from nginx's own access logs, aggregated on
the server with [GoAccess](https://goaccess.io).

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

## If you ever want more

The natural next step is [Plausible](https://plausible.io) — ~1KB, cookieless,
no consent banner, self-hostable. It would give per-page and live figures, at
the cost of a script on the page and being blockable by some lists (avoidable by
proxying it through this domain).

If that happens, add an `analytics` field to `siteconf.py` and a conditional
script tag in `templates/base.html`, so it stays one line to enable or remove.
