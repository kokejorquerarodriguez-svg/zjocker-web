#!/usr/bin/env python3
"""
Actualiza las metricas en vivo de index.html (zjocker-web) a partir de un
JSON con los datos recien obtenidos de las paginas publicas de Spotify y YouTube.

Uso:
    python3 update_metrics.py data.json index.html

El JSON debe tener esta forma (todos los campos son opcionales; si un campo
no viene, ese bloque no se toca):

{
  "monthly_listeners": "600K",
  "youtube_subs": "164K",
  "video_count": "70",
  "latest": [
    {"id": "xxxxxxxxxxx", "alt": "Titulo corto", "title": "Titulo completo (Video Oficial)",
     "time_es": "Hace 3 dias", "time_en": "3 days ago", "views": "10K"},
    ... (hasta 3 items, en orden cronologico del mas nuevo al mas viejo)
  ],
  "top10": [
    {"id": "xxxxxxxxxxx", "alt": "Titulo corto", "title": "Titulo completo",
     "time_es": "3 anios", "time_en": "3 years", "views": "19M", "rank": 1},
    ... (hasta 10 items, ordenados por vistas de mayor a menor)
  ]
}
"""
import json
import re
import sys


def build_stat_div(strong, es, en):
    return f'<div><strong>{strong}</strong><span class="lang-es">{es}</span><span class="lang-en">{en}</span></div>'


def replace_marked(html, tag, new_inner):
    start = f'<!-- {tag}:START -->'
    end = f'<!-- {tag}:END -->'
    si = html.find(start)
    ei = html.find(end)
    if si == -1 or ei == -1:
        print(f'WARNING: markers for {tag} not found, skipping')
        return html
    ei_full = ei + len(end)
    return html[:si] + start + new_inner + end + html[ei_full:]


def build_latest_card(item):
    return (
        f'<a class="yt-card" href="https://www.youtube.com/watch?v={item["id"]}" target="_blank" rel="noopener" '
        f'onclick="return openYouTube(event,\'https://www.youtube.com/watch?v={item["id"]}\')">\n'
        f'        <div class="yt-thumb"><span class="yt-date">NEW</span>'
        f'<img src="https://img.youtube.com/vi/{item["id"]}/hqdefault.jpg" alt="{item["alt"]}"></div>\n'
        f'        <div class="yt-info"><h3>{item["title"]}</h3>\n'
        f'          <div class="yt-meta"><span><span class="lang-es">{item["time_es"]}</span>'
        f'<span class="lang-en">{item["time_en"]}</span></span>'
        f'<b>{item["views"]} <span class="lang-es">vistas</span><span class="lang-en">views</span></b></div></div>\n'
        f'      </a>'
    )


def build_top10_card(item):
    return (
        f'<a class="yt-card" href="https://www.youtube.com/watch?v={item["id"]}" target="_blank" rel="noopener" '
        f'onclick="return openYouTube(event,\'https://www.youtube.com/watch?v={item["id"]}\')">\n'
        f'        <div class="yt-thumb"><span class="yt-rank">#{item["rank"]}</span>'
        f'<img src="https://img.youtube.com/vi/{item["id"]}/hqdefault.jpg" alt="{item["alt"]}"></div>\n'
        f'        <div class="yt-info"><h3>{item["title"]}</h3>\n'
        f'          <div class="yt-meta"><span><span class="lang-es">{item["time_es"]}</span>'
        f'<span class="lang-en">{item["time_en"]}</span></span>'
        f'<b>{item["views"]} <span class="lang-es">vistas</span><span class="lang-en">views</span></b></div></div>\n'
        f'      </a>'
    )


def main():
    if len(sys.argv) != 3:
        print('Uso: python3 update_metrics.py data.json index.html')
        sys.exit(1)

    data_path, html_path = sys.argv[1], sys.argv[2]

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    if 'monthly_listeners' in data:
        new_div = build_stat_div(data['monthly_listeners'], 'Oyentes mensuales', 'Monthly listeners')
        html = replace_marked(html, 'STAT:MONTHLY_LISTENERS', new_div)

    if 'youtube_subs' in data:
        new_div = build_stat_div(data['youtube_subs'], 'Suscriptores YouTube', 'YouTube subscribers')
        html = replace_marked(html, 'STAT:YT_SUBS', new_div)

    if 'video_count' in data:
        new_div = build_stat_div(data['video_count'], 'Videos oficiales', 'Official videos')
        html = replace_marked(html, 'STAT:VIDEO_COUNT', new_div)

    if 'latest' in data and data['latest']:
        cards = [build_latest_card(it) for it in data['latest'][:3]]
        inner = '<div class="yt-grid latest-grid">\n      ' + '\n      '.join(cards) + '\n    </div>'
        html = replace_marked(html, 'LATEST', inner)

    if 'top10' in data and data['top10']:
        cards = [build_top10_card(it) for it in data['top10'][:10]]
        inner = '<div class="yt-grid">\n\n      ' + '\n\n      '.join(cards) + '\n\n    </div>'
        html = replace_marked(html, 'TOP10', inner)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print('OK: index.html actualizado')


if __name__ == '__main__':
    main()
