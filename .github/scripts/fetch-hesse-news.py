#!/usr/bin/env python3
"""
Hesse Research Daily News Fetcher
Runs in GitHub Actions (US/EU runners, no GFW restrictions)
Primary sources: hermann-hesse.de, OpenAlex, CrossRef, official announcements
Output: daily/YYYY/MM/YYYY-MM-DD.md + README index update
"""

import requests
import json
import re
import os
import sys
from datetime import datetime, timezone, timedelta
from html import unescape

# Suppress SSL warnings for some sites
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Config ──
CACHE_TTL_HOURS = 12
MAX_ARTICLES_PER_CATEGORY = 8

# ── Primary Sources ──

def fetch_url(url, timeout=20, headers=None):
    """Generic URL fetcher."""
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; HesseResearchBot/1.0; +https://github.com/skyflyld/hesse-research)'
    }
    if headers:
        default_headers.update(headers)
    try:
        resp = requests.get(url, headers=default_headers, timeout=timeout, verify=False)
        resp.raise_for_status()
        # Try UTF-8 first
        if resp.encoding and resp.encoding.lower() != 'utf-8':
            resp.encoding = 'utf-8'
        return resp.text
    except Exception as e:
        print(f"  ⚠️  {url[:80]}: {str(e)[:80]}", file=sys.stderr)
        return None

def fetch_hermann_hesse():
    """Fetch official hermann-hesse.de news/events page."""
    items = []
    url = 'https://www.hermann-hesse.de/'
    print("  🔄 hermann-hesse.de...", end=' ')
    html = fetch_url(url)
    if not html:
        print('❌')
        return items
    
    # Look for news items in the page content
    # The site structure uses WordPress-like patterns
    
    # Try to find news/article links
    news_patterns = [
        r'<a[^>]*href="([^"]*hermann-hesse\.de[^"]*(?:news|aktuell|veranstaltung|beitrag)[^"]*)"[^>]*>([^<]+)</a>',
        r'<a[^>]*href="(https?://[^"]*(?:hermann-hesse\.de)[^"]*(?:\d{4}/\d{2}/\d{2})[^"]*)"[^>]*>([^<]+)</a>',
        r'<h[2-4][^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>\s*</h[2-4]>',
    ]
    
    found_titles = set()
    for pattern in news_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for m in matches:
            link = m[0].strip()
            title = unescape(re.sub(r'<[^>]+>', '', m[1]).strip())
            # Deduplicate
            key = title.lower()[:60]
            if key not in found_titles and len(title) > 5:
                found_titles.add(key)
                if not link.startswith('http'):
                    link = 'https://www.hermann-hesse.de' + link if link.startswith('/') else 'https://www.hermann-hesse.de/' + link
                items.append({
                    'title': title,
                    'url': link,
                    'source': 'hermann-hesse.de',
                })
    
    if items:
        print(f'✅ {len(items)} items')
    else:
        # Try parsing for any notable keyword matches in text
        print(f'⚠️  raw scan (no structured news found)')
        # Still return success - site is up but may not have current news
    
    return items

def fetch_open_alex():
    """Fetch new Hesse-related publications via OpenAlex API (free, open scholarly index)."""
    items = []
    url = (
        'https://api.openalex.org/works?'
        'filter=title_and_abstract.search:%22Hermann+Hesse%22,'
        'from_publication_date:2025-01-01&'
        'sort=publication_date:desc&'
        'per_page=25'
    )
    print("  🔄 OpenAlex API...", end=' ')
    data = fetch_url(url, headers={'Accept': 'application/json'})
    if not data:
        print('❌')
        return items
    
    try:
        result = json.loads(data)
        works = result.get('results', [])
        for w in works:
            title = w.get('title', '')
            if not title:
                continue
            doi = w.get('doi', '')
            doi_short = doi.replace('https://doi.org/', '') if doi else ''
            pub_date = w.get('publication_date', '')
            authors = []
            for auth in w.get('authorships', []):
                name = auth.get('author', {}).get('display_name', '')
                if name:
                    authors.append(name)
            source_info = w.get('primary_location', {}).get('source', {}) or {}
            journal = source_info.get('display_name', '') if source_info else ''
            
            # Build URL
            if doi:
                url = f'https://doi.org/{doi_short}'
            else:
                url = w.get('id', '').replace('https://', '')
            
            items.append({
                'title': title,
                'url': url,
                'source': f'OpenAlex',
                'journal': journal,
                'authors': ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else ''),
                'date': pub_date,
                'doi': doi_short,
            })
        
        print(f'✅ {len(works)} works')
    except Exception as e:
        print(f'❌ parse error: {e}')
    
    return items

def fetch_crossref():
    """Fetch Hesse-related DOIs via Crossref API."""
    items = []
    # Use a broad query to catch Hesse-related works
    url = (
        'https://api.crossref.org/works?'
        'query.title=Hermann+Hesse&'
        'filter=from-pub-date:2025-01-01&'
        'sort=published&order=desc&'
        'rows=15'
    )
    print("  🔄 Crossref API...", end=' ')
    data = fetch_url(url, headers={'Accept': 'application/json'})
    if not data:
        print('❌')
        return items
    
    try:
        result = json.loads(data)
        works = result.get('message', {}).get('items', [])
        for w in works:
            title_list = w.get('title', [])
            if not title_list:
                continue
            title = title_list[0]
            doi = w.get('DOI', '')
            authors = []
            for a in w.get('author', []):
                name = ' '.join(filter(None, [a.get('given', ''), a.get('family', '')]))
                if name:
                    authors.append(name)
            journal = w.get('container-title', [''])[0] if w.get('container-title') else ''
            pub_date_parts = w.get('published-print', {}).get('date-parts', [[]])[0]
            pub_date = '-'.join(str(p) for p in pub_date_parts) if pub_date_parts else ''
            
            items.append({
                'title': title,
                'url': f'https://doi.org/{doi}' if doi else '',
                'source': f'Crossref',
                'journal': journal,
                'authors': ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else ''),
                'date': pub_date,
                'doi': doi,
            })
        
        print(f'✅ {len(works)} works')
    except Exception as e:
        print(f'❌ parse error: {e}')
    
    return items

def fetch_bibliographia_hesseana():
    """Check Swiss National Library Bibliographia Hesseana for updates."""
    items = []
    # Bibliographia Hesseana is maintained by the Swiss National Library
    urls_to_check = [
        'https://www.nb.admin.ch/snl/en/home/research-portal/bibliographia-hesseana.html',
        'https://www.hermann-hesse.ch/bibliographie/',
    ]
    for url in urls_to_check:
        print(f"  🔄 {url[url.rfind('/')+1:]}...", end=' ')
        html = fetch_url(url)
        if html:
            print('✅')
            # Check for update indicators
            update_patterns = [
                r'(?:aktuell|update|neu|erschienen|publiziert)[^.]{0,100}(?:\d{4})',
                r'(?:2025|2026)[^.]{0,100}(?:Hesse|Bibliographie)',
            ]
            for pat in update_patterns:
                matches = re.findall(pat, html, re.IGNORECASE)
                for m in matches[:3]:
                    items.append({
                        'title': m.strip()[:120],
                        'url': url,
                        'source': 'Bibliographia Hesseana',
                    })
                    break  # One per pattern
        else:
            print('❌')
    
    return items

def fetch_hesse_gesellschaft():
    """Check Hesse-Gesellschaft for announcements."""
    items = []
    urls = [
        'https://www.hesse-gesellschaft.de/',
        'https://www.hesse-gesellschaft.de/aktuelles/',
    ]
    for url in urls:
        short = url.replace('https://www.hesse-gesellschaft.de', '')
        print(f"  🔄 Hesse-Gesellschaft{short}...", end=' ')
        html = fetch_url(url)
        if not html:
            print('❌')
            continue
        
        # Find links to news/articles
        pattern = r'<a[^>]*href="([^"]+)"[^>]*>([^<]{10,})</a>'
        matches = re.findall(pattern, html)
        found = 0
        for link, text in matches:
            text = unescape(text.strip())
            # Filter for relevant content
            keywords = ['hesse', 'tagung', 'vortrag', 'jahrbuch', 'preis', 'mitteilung',
                       'silser', 'hesse-tage', 'konferenz', 'call', 'beitrag']
            if any(kw in text.lower() for kw in keywords):
                full_url = link if link.startswith('http') else 'https://www.hesse-gesellschaft.de' + link
                items.append({
                    'title': text[:120],
                    'url': full_url,
                    'source': 'Hesse-Gesellschaft',
                })
                found += 1
                if found >= 5:
                    break
        
        if found:
            print(f'✅ {found} items')
        else:
            print(f'⚠️  page up, no structured news')
    
    return items

def fetch_silser_hesse_tage():
    """Check for Sils Hesse-Tage updates."""
    items = []
    urls = [
        'https://www.sils.ch/hesse-tage/',
        'https://www.hermann-hesse.ch/hesse-tage/',
    ]
    for url in urls:
        print(f"  🔄 Sils Hesse-Tage...", end=' ')
        html = fetch_url(url)
        if html:
            print('✅')
            # Look for program dates, speakers, themes
            patterns = [
                r'(?:2026|2027)[^.]{0,200}(?:Hesse|Tag|Programm|Thema|Vortrag)',
                r'(?:Programm|Thema|Referent|Vortrag)[^.]{0,200}',
            ]
            for pat in patterns:
                matches = re.findall(pat, html, re.IGNORECASE)
                for m in matches[:3]:
                    items.append({
                        'title': m.strip()[:120],
                        'url': url,
                        'source': 'Silser Hesse-Tage',
                    })
                    break
        else:
            print('❌')
    
    return items

def fetch_hesse_museum():
    """Check Hesse Museum Montagnola for exhibitions/events."""
    items = []
    urls = [
        'https://www.hessemuseum.ch/',
        'https://www.hessemuseum.ch/ausstellungen/',
        'https://www.hessemuseum.ch/veranstaltungen/',
    ]
    for url in urls:
        short = url.replace('https://www.hessemuseum.ch', '')
        print(f"  🔄 Hesse Museum{short}...", end=' ')
        html = fetch_url(url)
        if html:
            print('✅')
            # Look for exhibition/event links
            pattern = r'<a[^>]*href="([^"]+)"[^>]*>([^<]{15,})</a>'
            matches = re.findall(pattern, html)
            found = 0
            for link, text in matches:
                text = unescape(text.strip())
                keywords = ['ausstellung', 'veranstaltung', 'führung', 'vortrag',
                           'isa', 'rabinovitch', 'sonder', 'museum', 'eintritt']
                if any(kw in text.lower() for kw in keywords):
                    full_url = link if link.startswith('http') else 'https://www.hessemuseum.ch' + link
                    items.append({
                        'title': text[:120],
                        'url': full_url,
                        'source': 'Hesse Museum',
                    })
                    found += 1
                    if found >= 3:
                        break
            if not found:
                print('   (no news items detected)')
        else:
            print('❌')
    
    return items

def fetch_hesse_handbook_updates():
    """Check for updates on the Hesse-Handbuch (Metzler)."""
    items = []
    url = 'https://link.springer.com/book/9783476059969'  # Metzler/Springer link
    print("  🔄 Hesse-Handbuch (Metzler)...", end=' ')
    html = fetch_url(url)
    if html:
        print('✅')
        # Check for new edition info, reviews, etc.
        patterns = [
            r'[^.]{0,100}(?:Hesse|Handbuch)[^.]{0,200}(?:2025|2026|Rezension|Review|Neuauflage)',
            r'(?:Rezension|Review|Besprechung)[^.]{0,200}(?:Hesse|Handbuch)',
        ]
        for pat in patterns:
            matches = re.findall(pat, html, re.IGNORECASE)
            for m in matches[:2]:
                items.append({
                    'title': m.strip()[:150],
                    'url': url,
                    'source': 'J.B. Metzler',
                })
                break
    else:
        print('❌')
    
    return items

# ── Updated workflow: fetch primary sources + publish ─────────────────

def get_today():
    """Get today's date in Berlin timezone (CEST)."""
    now = datetime.now(timezone.utc) + timedelta(hours=2)
    return now

def has_existing_entry(year, month, day_str):
    """Check if a daily entry already exists."""
    return os.path.exists(f'{year}/{month}/{day_str}.md')

def classify_item(item):
    """Classify a source/item into a report category."""
    source = item.get('source', '').lower()
    title = item.get('title', '').lower()
    
    # Official announcements
    if any(s in source for s in ['hermann-hesse', 'hesse museum', 'bibliographia']):
        return '📢 Official'
    
    # Events
    if any(s in source for s in ['hesse-gesellschaft', 'silser', 'tagung', 'konferenz']):
        return '🗓️ Events'
    if any(kw in title for kw in ['tagung', 'konferenz', 'call', 'symposium', 'workshop', 'vortrag']):
        return '🗓️ Events'
    
    # New publications
    if any(s in source for s in ['openalex', 'crossref']):
        return '📄 New Publications'
    if any(kw in title for kw in ['buch', 'monographie', 'dissertation', 'aufsatz', 'essay']):
        return '📄 New Publications'
    
    # Reviews / media coverage
    if any(kw in title for kw in ['rezension', 'review', 'interview', 'besprechung']):
        return '📰 Media & Reviews'
    
    # Academic / research
    if any(s in source for s in ['metzler', 'springer', 'de gruyter']):
        return '📚 Academic'
    
    # Exhibition / museum
    if any(kw in title for kw in ['ausstellung', 'exhibition', 'museum', 'führung']):
        return '🎨 Exhibitions'
    
    return '📰 Other'

def generate_report(date, weekday_cn, weekday_de, year, month, categorized):
    """Generate the daily Markdown report."""
    lines = []
    lines.append(f"# 📡 黑塞研究前沿 · 每日信源")
    lines.append(f"# Hesse Research Front · Daily Primary Sources")
    lines.append(f"")
    lines.append(f"**📅 {date}（{weekday_cn}） | {weekday_de}**")
    lines.append(f"> 🦞 自动采集 · Hesse Research News Aggregator")
    lines.append(f"> 信源: hermann-hesse.de · OpenAlex · Crossref · Hesse-Gesellschaft · Hesse Museum")
    lines.append(f"> ℹ️ 所有条目均指向原始信源，保留一手可追溯性")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    
    total_count = 0
    
    # Category order
    cat_order = [
        '📢 Official',
        '📄 New Publications',
        '🗓️ Events',
        '📚 Academic',
        '📰 Media & Reviews',
        '🎨 Exhibitions',
        '📰 Other',
    ]
    
    for cat in cat_order:
        if cat not in categorized:
            continue
        items = categorized[cat]
        if not items:
            continue
        total_count += len(items)
        
        lines.append(f"## {cat}")
        lines.append(f"")
        
        for i, item in enumerate(items[:MAX_ARTICLES_PER_CATEGORY], 1):
            title = item['title']
            url = item.get('url', '')
            source = item.get('source', '')
            extra = ''
            
            if item.get('authors'):
                extra += f" · 👤 {item['authors']}"
            if item.get('journal'):
                extra += f" · 📖 {item['journal']}"
            if item.get('doi'):
                extra += f" · DOI: `{item['doi']}`"
            
            icon = '❶❷❸❹❺❻❼❽'[i-1] if i <= 8 else f'{i}.'
            
            if url:
                # GitHub renders links in markdown
                lines.append(f"{icon} **[{title}]({url})**")
            else:
                lines.append(f"{icon} **{title}**")
            
            lines.append(f"   _Source: {source}_{extra}")
            lines.append(f"")
    
    if total_count == 0:
        lines.append(f"_No new primary sources detected today._")
        lines.append(f"")
    
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*📡 Primary sources checked: hermann-hesse.de · OpenAlex · Crossref · Hesse-Gesellschaft · Hesse Museum · Bibliographia Hesseana · Silser Hesse-Tage*")
    lines.append(f"*🦞 Automatically collected on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC*")
    lines.append(f"")
    lines.append(f"> 🔗 [Research Overview](https://github.com/skyflyld/hesse-research) | [All Daily Reports](https://github.com/skyflyld/hesse-research/tree/main/daily)")
    lines.append(f"")
    
    return '\n'.join(lines), total_count

def update_readme_index(year, month, date_str, month_de, month_cn, day_num):
    """Add today's entry to README.md index."""
    readme_path = 'README.md'
    if not os.path.exists(readme_path):
        return
    
    entry_link = f"  - [{day_num}. {month_de}](daily/{year}/{month}/{date_str}.md)"
    month_header = f"### {month_de} · {month_cn}"
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme = f.read()
    
    # Check if already exists
    if f'](daily/{year}/{month}/{date_str}.md)' in readme:
        print(f"⚠️  Entry {date_str} already in README")
        return
    
    if month_header in readme:
        # Add after the month header
        lines_r = readme.split('\n')
        new_lines = []
        added = False
        for line in lines_r:
            new_lines.append(line)
            if line.strip() == month_header and not added:
                new_lines.append(entry_link)
                added = True
        if added:
            readme = '\n'.join(new_lines)
    else:
        # Add new month section
        separator_idx = readme.find('\n---\n')
        if separator_idx > 0:
            insertion = f"\n{month_header}\n{entry_link}\n"
            readme = readme[:separator_idx] + insertion + readme[separator_idx:]
        else:
            readme += f"\n{month_header}\n{entry_link}\n"
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)
    print(f"✅ README index updated")

def update_homepage_index(year, month, date_str, month_de, month_cn, day_num):
    """Add today's entry to the homepage index.md."""
    index_path = 'index.md'
    if not os.path.exists(index_path):
        return
    
    entry_link = f"  - [{day_num}. {month_de} · 每日信源](daily/{year}/{month}/{date_str}.md)"
    month_header = f"### {month_de} · {month_cn}"
    
    with open(index_path, 'r', encoding='utf-8') as f:
        index = f.read()
    
    # Check if already exists
    if f'](daily/{year}/{month}/{date_str}.md)' in index:
        print(f"⚠️  Entry {date_str} already in index.md")
        return
    
    if month_header in index:
        lines_r = index.split('\n')
        new_lines = []
        added = False
        for line in lines_r:
            new_lines.append(line)
            if line.strip() == month_header and not added:
                new_lines.append(entry_link)
                added = True
        if added:
            index = '\n'.join(new_lines)
    else:
        # Find the daily archive section
        archive_section_start = None
        for i, line in enumerate(lines_r if 'lines_r' in dir() else index.split('\n')):
            if '每日追踪 · Archiv' in line or '每日信源 · Daily' in line:
                archive_section_start = i
        
        if archive_section_start is not None:
            insertion = f"\n{month_header}\n{entry_link}\n"
            index_lines = index.split('\n')
            insert_pos = archive_section_start + 2  # After the section header
            index = '\n'.join(index_lines[:insert_pos]) + insertion + '\n'.join(index_lines[insert_pos:])
        else:
            index += f"\n### {month_header}\n{entry_link}\n"
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index)
    print(f"✅ index.md updated")


def main():
    today = get_today()
    date_str = today.strftime('%Y-%m-%d')
    weekday_cn = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][today.weekday()]
    weekday_de = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'][today.weekday()]
    year = today.strftime('%Y')
    month = today.strftime('%m')
    day_num = today.strftime('%d').lstrip('0')
    
    # German month names
    month_names_de = {
        '01': 'Januar', '02': 'Februar', '03': 'März', '04': 'April',
        '05': 'Mai', '06': 'Juni', '07': 'Juli', '08': 'August',
        '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Dezember'
    }
    month_names_cn = {
        '01': '一月', '02': '二月', '03': '三月', '04': '四月',
        '05': '五月', '06': '六月', '07': '七月', '08': '八月',
        '09': '九月', '10': '十月', '11': '十一月', '12': '十二月'
    }
    month_de = month_names_de.get(month, month)
    month_cn = month_names_cn.get(month, month)
    
    print(f"🔬 Hesse Research News Fetch — {date_str}")
    
    # ── Skip if today's entry already exists ──
    output_dir = f"daily/{year}/{month}"
    output_path = f"{output_dir}/{date_str}.md"
    
    if os.path.exists(output_path):
        print(f"⚠️  Entry {date_str} already exists, skipping fetch")
        # Just update index if needed
        update_readme_index(year, month, date_str, month_de, month_cn, day_num)
        update_homepage_index(year, month, date_str, month_de, month_cn, day_num)
        print(f"✅ Done (update only)")
        return
    
    # ── Fetch all primary sources ──
    all_items = []
    
    # 1. Official site
    items = fetch_hermann_hesse()
    for item in items:
        item['source'] = 'hermann-hesse.de'
    all_items.extend(items)
    
    # 2. OpenAlex (academic publications)
    items = fetch_open_alex()
    for item in items:
        item['source'] = 'OpenAlex'
    all_items.extend(items)
    
    # 3. Crossref
    items = fetch_crossref()
    for item in items:
        item['source'] = 'Crossref'
    all_items.extend(items)
    
    # 4. Hesse Gesellschaft
    items = fetch_hesse_gesellschaft()
    for item in items:
        item['source'] = 'Hesse-Gesellschaft'
    all_items.extend(items)
    
    # 5. Hesse Museum
    items = fetch_hesse_museum()
    for item in items:
        item['source'] = 'Hesse Museum'
    all_items.extend(items)
    
    # 6. Bibliographia Hesseana
    items = fetch_bibliographia_hesseana()
    all_items.extend(items)
    
    # 7. Silser Hesse-Tage
    items = fetch_silser_hesse_tage()
    all_items.extend(items)
    
    # 8. Hesse-Handbuch updates
    items = fetch_hesse_handbook_updates()
    all_items.extend(items)
    
    print(f"\n📊 Total: {len(all_items)} primary-source items")
    
    # Deduplicate by title
    seen_titles = set()
    unique_items = []
    for item in all_items:
        key = item['title'][:80].lower().strip()
        if key not in seen_titles:
            seen_titles.add(key)
            unique_items.append(item)
    
    print(f"📊 Unique: {len(unique_items)}")
    
    # ── Classify ──
    categorized = {}
    for item in unique_items:
        cat = classify_item(item)
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(item)
    
    print(f"📂 Categories: {len(categorized)}")
    for cat, items in sorted(categorized.items()):
        print(f"   {cat}: {len(items)}")
    
    # ── Generate report ──
    os.makedirs(output_dir, exist_ok=True)
    
    report, total_count = generate_report(date_str, weekday_cn, weekday_de, year, month, categorized)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Report: {output_path}")
    print(f"📊 Items: {total_count}")
    
    # ── Update indices ──
    update_readme_index(year, month, date_str, month_de, month_cn, day_num)
    update_homepage_index(year, month, date_str, month_de, month_cn, day_num)
    
    print(f"\n🎉 Done!")

if __name__ == '__main__':
    main()
