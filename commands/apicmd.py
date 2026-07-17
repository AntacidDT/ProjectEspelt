import time


def _http_get(host, path, timeout=10):
    import usocket
    sock = usocket.socket()
    sock.settimeout(timeout)
    addr = usocket.getaddrinfo(host, 80)[0][-1]
    sock.connect(addr)
    req = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nUser-Agent: espelt\r\nAccept: */*\r\n\r\n'
    sock.sendall(req.encode())
    data = b''
    while True:
        try:
            chunk = sock.read(1024)
        except OSError:
            break
        if not chunk:
            break
        data += chunk
    try:
        sock.close()
    except Exception:
        pass
    raw = data.decode('utf-8', 'ignore')

    header_end = raw.find('\r\n\r\n')
    if header_end < 0:
        header_end = raw.find('\n\n')
    if header_end < 0:
        return raw

    headers = raw[:header_end]
    body = raw[header_end + 4:].lstrip('\r\n')

    if 'Transfer-Encoding: chunked' in headers:
        decoded = b''
        pos = 0
        body_bytes = body.encode('utf-8', 'ignore')
        while pos < len(body_bytes):
            crlf_pos = body_bytes.find(b'\r\n', pos)
            if crlf_pos < 0:
                break
            try:
                chunk_size = int(body_bytes[pos:crlf_pos], 16)
            except ValueError:
                break
            if chunk_size == 0:
                break
            decoded += body_bytes[crlf_pos + 2:crlf_pos + 2 + chunk_size]
            pos = crlf_pos + 2 + chunk_size + 2
        body = decoded.decode('utf-8', 'ignore')

    status_line = headers.split('\r\n')[0] if headers else ''
    if '301' in status_line or '302' in status_line or '307' in status_line or '308' in status_line:
        for line in headers.split('\r\n'):
            if line.lower().startswith('location:'):
                loc = line.split(':', 1)[1].strip()
                if loc.startswith('http://'):
                    new_host = loc[7:].split('/')[0]
                    new_path = loc[7 + len(new_host):]
                    return _http_get(new_host, new_path, timeout)
                elif loc.startswith('https://'):
                    new_host = loc[8:].split('/')[0]
                    new_path = loc[8 + len(new_host):]
                    return _https_get(new_host, new_path, timeout)
                elif loc.startswith('/'):
                    return _http_get(host, loc, timeout)
                break

    return body


def _https_get(host, path, timeout=10):
    import usocket
    import ssl
    sock = usocket.socket()
    sock.settimeout(timeout)
    addr = usocket.getaddrinfo(host, 443)[0][-1]
    sock.connect(addr)
    ssock = ssl.wrap_socket(sock, server_hostname=host)
    req = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nUser-Agent: espelt\r\nAccept: application/json\r\n\r\n'
    ssock.sendall(req.encode())
    data = b''
    while True:
        try:
            chunk = ssock.read(1024)
        except OSError:
            break
        if not chunk:
            break
        data += chunk
    try:
        ssock.close()
    except Exception:
        pass
    raw = data.decode('utf-8', 'ignore')

    header_end = raw.find('\r\n\r\n')
    if header_end < 0:
        header_end = raw.find('\n\n')
    if header_end < 0:
        return raw

    headers = raw[:header_end]
    status_line = headers.split('\r\n')[0] if headers else ''
    body = raw[header_end + 4:].lstrip('\r\n')

    if 'Transfer-Encoding: chunked' in headers:
        decoded = b''
        pos = 0
        body_bytes = body.encode('utf-8', 'ignore')
        while pos < len(body_bytes):
            crlf_pos = body_bytes.find(b'\r\n', pos)
            if crlf_pos < 0:
                break
            try:
                chunk_size = int(body_bytes[pos:crlf_pos], 16)
            except ValueError:
                break
            if chunk_size == 0:
                break
            decoded += body_bytes[crlf_pos + 2:crlf_pos + 2 + chunk_size]
            pos = crlf_pos + 2 + chunk_size + 2
        body = decoded.decode('utf-8', 'ignore')

    if '301' in status_line or '302' in status_line or '307' in status_line or '308' in status_line:
        for line in headers.split('\r\n'):
            if line.lower().startswith('location:'):
                loc = line.split(':', 1)[1].strip()
                if loc.startswith('https://'):
                    new_host = loc[8:].split('/')[0]
                    new_path = loc[8 + len(new_host):]
                    return _https_get(new_host, new_path, timeout)
                elif loc.startswith('/'):
                    return _https_get(host, loc, timeout)
                break

    return body


def _https_post(host, path, payload, timeout=30):
    import usocket
    import ssl
    sock = usocket.socket()
    sock.settimeout(timeout)
    addr = usocket.getaddrinfo(host, 443)[0][-1]
    sock.connect(addr)
    ssock = ssl.wrap_socket(sock, server_hostname=host)
    request = (
        f'POST {path} HTTP/1.1\r\n'
        f'Host: {host}\r\n'
        f'Content-Type: application/json\r\n'
        f'Content-Length: {len(payload)}\r\n'
        f'Connection: close\r\n'
        f'\r\n'
        f'{payload}'
    )
    ssock.sendall(request.encode())
    data = b''
    while True:
        try:
            chunk = ssock.read(2048)
        except OSError:
            break
        if not chunk:
            break
        data += chunk
    try:
        ssock.close()
    except Exception:
        pass
    raw = data.decode('utf-8', 'ignore')

    header_end = raw.find('\r\n\r\n')
    if header_end < 0:
        header_end = raw.find('\n\n')
    if header_end < 0:
        return raw

    headers = raw[:header_end]
    body = raw[header_end + 4:].lstrip('\r\n')

    if 'Transfer-Encoding: chunked' in headers:
        decoded = b''
        pos = 0
        body_bytes = body.encode('utf-8', 'ignore')
        while pos < len(body_bytes):
            crlf_pos = body_bytes.find(b'\r\n', pos)
            if crlf_pos < 0:
                break
            try:
                chunk_size = int(body_bytes[pos:crlf_pos], 16)
            except ValueError:
                break
            if chunk_size == 0:
                break
            decoded += body_bytes[crlf_pos + 2:crlf_pos + 2 + chunk_size]
            pos = crlf_pos + 2 + chunk_size + 2
        body = decoded.decode('utf-8', 'ignore')

    return body


def _wrap_text(text, width):
    words = text.split()
    lines = []
    line = ''
    for w in words:
        test = (line + ' ' + w).strip() if line else w
        if len(test) <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def cmd_detailwiki(args):
    query = args.strip()
    if not query:
        return ('print', 'wiki: usage: wiki [query]')
    try:
        import ujson
        host = 'en.wikipedia.org'
        path = '/w/api.php?action=query&titles={}&prop=extracts&exintro=true&explaintext=true&format=json&redirects=1'.format(
            query.replace(' ', '%20'))
        body = _https_get(host, path)
        j = ujson.loads(body)
        pages = j.get('query', {}).get('pages', {})
        if not pages:
            return ('print', f'wiki: no results for "{query}"')
        page = list(pages.values())[0]
        if page.get('pageid', -1) < 0 or 'extract' not in page:
            search_path = '/w/api.php?action=query&list=search&srsearch={}&srlimit=1&format=json'.format(
                query.replace(' ', '%20'))
            body2 = _https_get(host, search_path)
            j2 = ujson.loads(body2)
            results = j2.get('query', {}).get('search', [])
            if not results:
                return ('print', f'wiki: no results for "{query}"')
            title = results[0].get('title', query)
            snippet = results[0].get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
            wrapped = _wrap_text(snippet, 36)
            lines = [f'=== {title} ===', ''] + ['  ' + l for l in wrapped]
            return ('print_lines', lines)
        title = page.get('title', query)
        extract = page.get('extract', 'No information available.')
        if len(extract) > 400:
            truncated = extract[:400]
            last_period = truncated.rfind('. ')
            if last_period > 200:
                truncated = truncated[:last_period + 1]
            else:
                truncated += '...'
            extract = truncated
        wrapped = _wrap_text(extract, 36)
        lines = [f'=== {title} ===', ''] + ['  ' + l for l in wrapped]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'wiki: {e}')


def cmd_timetable(args):
    try:
        import ujson
        body = _https_get('red.epodra.net', '/api/timetable')
        j = ujson.loads(body)
        lines = ['=== Today\'s Timetable ===']
        for entry in j if isinstance(j, list) else []:
            name = entry.get('subject', entry.get('name', '?'))
            time_s = entry.get('time', '')
            lines.append(f'  {time_s} {name}')
        if len(lines) == 1:
            lines.append('  (no timetable data)')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'timetable: {e}')


def _url_encode(s):
    """Simple URL encoder for MicroPython (no urllib)."""
    safe = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.~'
    out = ''
    for c in s:
        if c in safe:
            out += c
        elif c == ' ':
            out += '%20'
        else:
            out += '%%%02X' % ord(c)
    return out


def cmd_prayer(args):
    city_arg = args.strip()
    # Default to Falkensee, Germany
    if city_arg:
        # Parse "city, country" format
        parts = city_arg.split(',')
        city = parts[0].strip()
        country = parts[1].strip() if len(parts) > 1 else 'Germany'
    else:
        city = 'Falkensee'
        country = 'Germany'
    try:
        import ujson
        import time as _time
        t = _time.localtime()
        date_str = f'{t[0]:04d}-{t[1]:02d}-{t[2]:02d}'
        # Include date to avoid 302 redirect
        path = '/v1/timingsByCity/{}?city={}&country={}&method=2'.format(
            date_str, _url_encode(city), _url_encode(country))
        body = _https_get('api.aladhan.com', path)
        j = ujson.loads(body)
        if j.get('code') != 200:
            return ('print', f'prayer: could not find "{city_arg}"')
        timings = j.get('data', {}).get('timings', {})
        date_info = j.get('data', {}).get('date', {})
        readable = date_info.get('readable', '')
        location_str = f'{city}, {country}' if city_arg else 'Falkensee, Germany'
        lines = [f'=== Prayer Times ({location_str}) ===']
        if readable:
            lines.append(f'  {readable}')
        for name in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
            t = timings.get(name, '?')
            lines.append(f'  {name:10s} {t}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'prayer: {e}')


def cmd_chat(args):
    """AI chat via Pollinations.ai (free, no auth). Usage: chat [message]"""
    msg = args.strip()
    if not msg:
        return ('print_lines', [
            'chat: usage: chat [message]',
            '',
            '  chat what is the capital of France',
            '  chat explain recursion in one sentence',
            '  chat write a haiku about robots',
        ])
    import usocket
    import ssl
    import ujson
    try:
        host = 'text.pollinations.ai'
        path = '/' + msg.replace(' ', '%20')
        sock = usocket.socket()
        sock.settimeout(15)
        addr = usocket.getaddrinfo(host, 443)[0][-1]
        sock.connect(addr)
        ssock = ssl.wrap_socket(sock, server_hostname=host)
        req = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'
        ssock.sendall(req.encode())
        data = b''
        while True:
            chunk = ssock.read(512)
            if not chunk:
                break
            data += chunk
        ssock.close()
        raw = data.decode()
        idx = raw.find('\r\n\r\n')
        body = raw[idx:].lstrip('\r\n') if idx >= 0 else raw
        # Response is plain text
        text = body.strip()
        if len(text) > 200:
            text = text[:200] + '...'
        return ('print_lines', ['  ' + line for line in text.split('\n') if line.strip()][:8])
    except Exception as e:
        return ('print', f'chat: {e}')


def cmd_translate(args):
    parts = args.strip().split(None, 2) if args.strip() else []
    if len(parts) < 3:
        return ('print_lines', [
            'translate: usage: translate [from] [to] [text]',
            '',
            '  Languages: en, de, fr, es, it, pt, nl, ru, ja, ko, zh, ar, tr',
            '',
            '  Example: translate en de hello world',
        ])
    src = parts[0]
    dst = parts[1]
    text = parts[2]
    try:
        import ure as re
        encoded = text.replace(' ', '%20')
        host = 'translate.googleapis.com'
        path = f'/translate_a/single?client=gtx&sl={src}&tl={dst}&dt=t&q={encoded}'
        body = _https_get(host, path, timeout=15)
        import ujson
        j = ujson.loads(body)
        if isinstance(j, list) and len(j) > 0 and isinstance(j[0], list):
            translated = ''.join(seg[0] for seg in j[0] if seg[0])
            return ('print_lines', [
                f'=== {src} -> {dst} ===',
                f'  {text}',
                f'  {translated}',
            ])
        return ('print', 'translate: could not parse response')
    except Exception as e:
        return ('print', f'translate: {e}')


def cmd_define(args):
    word = args.strip()
    if not word:
        return ('print', 'define: usage: define [word]')
    try:
        body = _https_get('api.dictionaryapi.dev', f'/api/v2/entries/en/{word}', timeout=10)
        import ujson
        j = ujson.loads(body)
        if not isinstance(j, list) or len(j) == 0:
            return ('print', f'define: no definition found for "{word}"')
        entry = j[0]
        word_text = entry.get('word', word)
        phonetic = entry.get('phonetic', '')
        lines = [f'=== {word_text} {phonetic} ===']
        meanings = entry.get('meanings', [])
        synonyms_all = []
        if meanings:
            primary = meanings[0]
            pos = primary.get('partOfSpeech', '')
            defs = primary.get('definitions', [])
            if defs:
                d = defs[0].get('definition', '')
                lines.append(f'  [{pos}] {d}')
                ex = defs[0].get('example', '')
                if ex:
                    lines.append(f'  e.g. "{ex[:80]}"')
                syns = defs[0].get('synonyms', [])
                if syns:
                    synonyms_all.extend(syns)
            for m in meanings:
                for d in m.get('definitions', []):
                    for s in d.get('synonyms', []):
                        if s not in synonyms_all:
                            synonyms_all.append(s)
                for s in m.get('synonyms', []):
                    if s not in synonyms_all:
                        synonyms_all.append(s)
            if len(meanings) > 1:
                pos2 = meanings[1].get('partOfSpeech', '')
                defs2 = meanings[1].get('definitions', [])
                if defs2:
                    d2 = defs2[0].get('definition', '')
                    lines.append(f'  [{pos2}] {d2}')
        if synonyms_all:
            lines.append(f'  Synonyms: {", ".join(synonyms_all[:6])}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'define: {e}')


def cmd_news(args):
    region = args.strip().lower() if args.strip() else 'us'
    feeds = {
        'us': ('BBC US', 'feeds.bbci.co.uk', '/news/world/us_and_canada/rss.xml'),
        'uk': ('BBC UK', 'feeds.bbci.co.uk', '/news/uk/rss.xml'),
        'world': ('BBC World', 'feeds.bbci.co.uk', '/news/world/rss.xml'),
        'tech': ('BBC Tech', 'feeds.bbci.co.uk', '/news/technology/rss.xml'),
        'science': ('BBC Science', 'feeds.bbci.co.uk', '/news/science_and_environment/rss.xml'),
        'de': ('BBC Germany', 'feeds.bbci.co.uk', '/news/world/europe/rss.xml'),
        'fr': ('BBC France', 'feeds.bbci.co.uk', '/news/world/europe/rss.xml'),
        'nl': ('BBC Europe', 'feeds.bbci.co.uk', '/news/world/europe/rss.xml'),
        'global': ('BBC World', 'feeds.bbci.co.uk', '/news/world/rss.xml'),
        'world': ('BBC World', 'feeds.bbci.co.uk', '/news/world/rss.xml'),
    }
    if region not in feeds:
        feeds[region] = ('BBC World', 'feeds.bbci.co.uk', '/news/world/rss.xml')
    label, host, path = feeds[region]
    try:
        body = _https_get(host, path, timeout=10)
        articles = _parse_rss(body)
        if not articles:
            return ('print', f'news: no headlines for "{region}"')
        lines = [f'=== {label} ===']
        for a in articles[:5]:
            title = a.get('title', 'No title')
            lines.append(f'')
            lines.append(f'  {title[:40]}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'news: {e}')


def cmd_stock(args):
    symbol = args.strip().upper()
    if not symbol:
        return ('print', 'stock: usage: stock [SYMBOL] (e.g. stock AAPL)')
    try:
        import ujson
        import usocket
        import ssl
        host = 'query1.finance.yahoo.com'
        path = f'/v8/finance/chart/{symbol}?interval=1d&range=1d'
        sock = usocket.socket()
        sock.settimeout(10)
        addr = usocket.getaddrinfo(host, 443)[0][-1]
        sock.connect(addr)
        ssock = ssl.wrap_socket(sock, server_hostname=host)
        req = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nUser-Agent: Mozilla/5.0\r\nAccept: application/json\r\n\r\n'
        ssock.sendall(req.encode())
        data = b''
        while True:
            try:
                chunk = ssock.read(1024)
            except:
                break
            if not chunk:
                break
            data += chunk
        ssock.close()
        raw = data.decode('utf-8', 'ignore')
        idx = raw.find('\r\n\r\n')
        body = raw[idx+4:].lstrip('\r\n') if idx >= 0 else raw
        j = ujson.loads(body)
        meta = j.get('chart', {}).get('result', [{}])[0].get('meta', {})
        price = meta.get('regularMarketPrice', 0)
        prev = meta.get('previousClose', 0)
        if not prev:
            prev = meta.get('chartPreviousClose', 0)
        name = meta.get('shortName', symbol)
        change = price - prev if prev else 0
        pct = (change / prev * 100) if prev else 0
        arrow = '+' if change >= 0 else ''
        v = change
        vp = pct
        ci = int(abs(v))
        cf = int(abs(v) * 100) % 100
        pi = int(abs(vp))
        pf = int(abs(vp) * 10) % 10
        c_str = str(ci) + '.' + str(cf // 10) + str(cf % 10)
        p_str = str(pi) + '.' + str(pf)
        return ('print', f'=== {name} ({symbol}) ===\n  ${price}\n  {arrow}{c_str} ({arrow}{p_str}%)')
    except Exception as e:
        return ('print', f'stock: {e}')


def cmd_crypto(args):
    symbol = args.strip().upper()
    if not symbol:
        return ('print', 'crypto: usage: crypto [SYMBOL] (e.g. crypto BTC)')
    coin_map = {
        'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
        'DOGE': 'dogecoin', 'ADA': 'cardano', 'XRP': 'ripple',
        'DOT': 'polkadot', 'MATIC': 'matic-network', 'AVAX': 'avalanche-2',
        'LINK': 'chainlink', 'UNI': 'uniswap', 'SHIB': 'shiba-inu',
        'LTC': 'litecoin', 'ATOM': 'cosmos', 'NEAR': 'near',
    }
    coin_id = coin_map.get(symbol, symbol.lower())
    try:
        import ujson
        path = f'/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true'
        body = _https_get('api.coingecko.com', path, timeout=10)
        j = ujson.loads(body)
        data = j.get(coin_id, {})
        if not data:
            return ('print', f'crypto: unknown symbol "{symbol}"')
        price = data.get('usd', 0)
        change = data.get('usd_24h_change', 0)
        arrow = '+' if change >= 0 else ''
        return ('print', f'=== {symbol} ===\n  ${price:,.2f}\n  {arrow}{change:.2f}% (24h)')
    except Exception as e:
        return ('print', f'crypto: {e}')


def cmd_timezone(args):
    city = args.strip()
    if not city:
        return ('print', 'timezone: usage: timezone [city]')
    tz_map = {
        'tokyo': 'Asia/Tokyo', 'berlin': 'Europe/Berlin', 'london': 'Europe/London',
        'new york': 'America/New_York', 'paris': 'Europe/Paris', 'sydney': 'Australia/Sydney',
        'dubai': 'Asia/Dubai', 'moscow': 'Europe/Moscow', 'beijing': 'Asia/Shanghai',
        'shanghai': 'Asia/Shanghai', 'mumbai': 'Asia/Kolkata', 'delhi': 'Asia/Kolkata',
        'singapore': 'Asia/Singapore', 'hong kong': 'Asia/Hong_Kong', 'seoul': 'Asia/Seoul',
        'amsterdam': 'Europe/Amsterdam', 'rome': 'Europe/Rome', 'madrid': 'Europe/Madrid',
        'toronto': 'America/Toronto', 'los angeles': 'America/Los_Angeles',
        'chicago': 'America/Chicago', 'denver': 'America/Denver',
        'sao paulo': 'America/Sao_Paulo', 'buenos aires': 'America/Argentina/Buenos_Aires',
        'cairo': 'Africa/Cairo', 'lagos': 'Africa/Lagos', 'nairobi': 'Africa/Nairobi',
        'bangkok': 'Asia/Bangkok', 'hanoi': 'Asia/Ho_Chi_Minh', 'jakarta': 'Asia/Jakarta',
        'istanbul': 'Europe/Istanbul', 'athens': 'Europe/Athens', 'warsaw': 'Europe/Warsaw',
        'vienna': 'Europe/Vienna', 'zurich': 'Europe/Zurich', 'stockholm': 'Europe/Stockholm',
        'oslo': 'Europe/Oslo', 'copenhagen': 'Europe/Copenhagen', 'helsinki': 'Europe/Helsinki',
        'dublin': 'Europe/Dublin', 'lisbon': 'Europe/Lisbon', 'prague': 'Europe/Prague',
        'budapest': 'Europe/Budapest', 'bucharest': 'Europe/Bucharest',
        'taipei': 'Asia/Taipei', 'kuala lumpur': 'Asia/Kuala_Lumpur',
        'auckland': 'Pacific/Auckland', 'perth': 'Australia/Perth',
        'mexico city': 'America/Mexico_City', 'bogota': 'America/Bogota',
        'lima': 'America/Lima', 'santiago': 'America/Santiago',
        'johannesburg': 'Africa/Johannesburg', 'cape town': 'Africa/Johannesburg',
        'tel aviv': 'Asia/Jerusalem', 'jeddah': 'Asia/Riyadh', 'riyadh': 'Asia/Riyadh',
    }
    key = city.lower()
    if key in tz_map:
        slug = tz_map[key]
    else:
        slug = city.replace(' ', '/')
    try:
        import ujson
        body = _https_get('timeapi.io', '/api/Time/current/zone?timeZone=' + slug, timeout=10)
        j = ujson.loads(body)
        if isinstance(j, str):
            return ('print', 'timezone: unknown city "' + city + '"')
        hour = j.get('hour', 0)
        minute = j.get('minute', 0)
        second = j.get('seconds', 0)
        date_s = j.get('date', '')
        tz_s = j.get('timeZone', city)
        ampm = 'AM' if hour < 12 else 'PM'
        hour12 = hour % 12 or 12
        m_str = str(minute) if minute > 9 else '0' + str(minute)
        s_str = str(second) if second > 9 else '0' + str(second)
        return ('print', '=== ' + tz_s + ' ===\n  ' + date_s + '\n  ' + str(hour12) + ':' + m_str + ':' + s_str + ' ' + ampm)
    except Exception as e:
        return ('print', 'timezone: ' + str(e))


def cmd_ipinfo(args):
    try:
        import usocket
        import ujson
        sock = usocket.socket()
        sock.settimeout(10)
        addr = usocket.getaddrinfo('ip-api.com', 80)[0][-1]
        sock.connect(addr)
        sock.sendall(b'GET /json/ HTTP/1.1\r\nHost: ip-api.com\r\nConnection: close\r\n\r\n')
        data = b''
        while True:
            try:
                chunk = sock.read(1024)
            except:
                break
            if not chunk:
                break
            data += chunk
        sock.close()
        raw = data.decode('utf-8', 'ignore')
        idx = raw.find('\r\n\r\n')
        body = raw[idx+4:].lstrip('\r\n') if idx >= 0 else raw
        j = ujson.loads(body)
        if j.get('status') == 'fail':
            return ('print', 'ipinfo: could not retrieve')
        lines = [
            '=== IP Info ===',
            f'  IP:       {j.get("query", "?")}',
            f'  City:     {j.get("city", "?")}',
            f'  Region:   {j.get("regionName", "?")}',
            f'  Country:  {j.get("country", "?")}',
            f'  ISP:      {j.get("isp", "?")}',
            f'  Lat/Lon:  {j.get("lat", "?")}, {j.get("lon", "?")}',
        ]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'ipinfo: {e}')


def cmd_exchange(args):
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 2:
        return ('print_lines', [
            'exchange: usage: exchange [amount] [from] [to]',
            '',
            '  Example: exchange 100 USD EUR',
            '  Example: exchange 50 GBP JPY',
            '',
            '  Common: USD, EUR, GBP, JPY, CHF, CAD, AUD, NLG',
        ])
    try:
        amount = float(parts[0])
    except ValueError:
        return ('print', 'exchange: invalid amount')
    from_cur = parts[1].upper()
    to_cur = parts[2].upper() if len(parts) > 2 else 'EUR'
    try:
        import ujson
        body = _https_get('open.er-api.com', f'/v6/latest/{from_cur}', timeout=10)
        j = ujson.loads(body)
        if j.get('result') != 'success':
            return ('print', f'exchange: unknown currency "{from_cur}"')
        rates = j.get('rates', {})
        if to_cur not in rates:
            return ('print', f'exchange: unknown currency "{to_cur}"')
        result = amount * rates[to_cur]
        rate = rates[to_cur]
        return ('print_lines', [
            f'=== Exchange ===',
            f'  {amount:.2f} {from_cur} = {result:.2f} {to_cur}',
            f'  1 {from_cur} = {rate:.4f} {to_cur}',
        ])
    except Exception as e:
        return ('print', f'exchange: {e}')


def cmd_gh(args):
    user = args.strip()
    if not user:
        return ('print', 'gh: usage: gh [username]')
    try:
        import ujson
        body = _https_get('api.github.com', f'/users/{user}', timeout=10)
        # Debug: show first 200 chars if parsing fails
        try:
            j = ujson.loads(body)
        except ValueError:
            # Show the body for debugging
            return ('print', f'gh: bad JSON. First 100 chars: {body[:100]}')
        if 'message' in j:
            return ('print', f'gh: {j["message"]}')
        name = j.get('name', '') or user
        bio = j.get('bio', '') or 'No bio'
        repos = j.get('public_repos', 0)
        followers = j.get('followers', 0)
        following = j.get('following', 0)
        location = j.get('location', '') or 'Unknown'
        created = j.get('created_at', '')[:10]
        lines = [
            f'=== {name} (@{user}) ===',
            f'  Bio:      {bio[:40]}',
            f'  Repos:    {repos}',
            f'  Followers: {followers}  Following: {following}',
            f'  Location: {location}',
            f'  Joined:   {created}',
        ]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'gh: {e}')


def cmd_ghrepo(args):
    user = args.strip()
    if not user:
        return ('print', 'ghrepo: usage: ghrepo [username]')
    try:
        import ujson
        body = _https_get('api.github.com', f'/users/{user}/repos?sort=stars&per_page=10', timeout=10)
        j = ujson.loads(body)
        if not isinstance(j, list):
            return ('print', f'ghrepo: {j.get("message", "error")}')
        if not j:
            return ('print', f'ghrepo: no repos for "{user}"')
        lines = [f'=== {user} repos ===']
        for r in j[:8]:
            stars = r.get('stargazers_count', 0)
            lang = r.get('language', '?') or '?'
            name = r.get('name', '?')
            lines.append(f'  {name} [{lang}] *{stars}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'ghrepo: {e}')


# German state codes (Bundesländer)
DE_STATES = {
    'BB': 'Brandenburg', 'BE': 'Berlin', 'BW': 'Baden-Württemberg',
    'BY': 'Bavaria', 'HB': 'Bremen', 'HE': 'Hesse',
    'HH': 'Hamburg', 'MV': 'Mecklenburg-Vorpommern',
    'NI': 'Lower Saxony', 'NW': 'North Rhine-Westphalia',
    'RP': 'Rhineland-Palatinate', 'SH': 'Schleswig-Holstein',
    'SL': 'Saarland', 'SN': 'Saxony', 'ST': 'Saxony-Anhalt',
    'TH': 'Thuringia',
}


def cmd_holiday(args):
    country = args.strip().upper() if args.strip() else 'NL'
    try:
        import ujson
        import time as _time
        t = _time.localtime()
        year = t[0]

        # Handle German state codes (DE-BW, DE-BY, etc.)
        if country.startswith('DE-') and len(country) == 5:
            state = country[3:]  # e.g. 'BW' from 'DE-BW'
            if state not in DE_STATES:
                return ('print', f'holiday: unknown state "{state}"\n  valid: {", ".join(DE_STATES.keys())}')
            # Fetch all DE holidays and filter
            body = _https_get('date.nager.at', f'/api/v3/PublicHolidays/{year}/DE', timeout=10)
            j = ujson.loads(body)
            # Filter for state-specific or nationwide
            state_code = f'DE-{state}'
            state_holidays = []
            for h in j:
                counties = h.get('counties', [])
                if not counties or state_code in counties or 'DE' in counties:
                    # Empty counties = nationwide, or state in list
                    state_holidays.append(h)
            j = state_holidays
            display_loc = f'DE ({DE_STATES[state]})'
        else:
            # Standard country lookup
            body = _https_get('date.nager.at', f'/api/v3/PublicHolidays/{year}/{country}', timeout=10)
            j = ujson.loads(body)
            display_loc = country

        if not isinstance(j, list) or len(j) == 0:
            return ('print', f'holiday: no holidays for "{country}"')
        now = f'{year:04d}-{t[1]:02d}-{t[2]:02d}'
        next_holiday = None
        for h in j:
            if h.get('date', '') >= now:
                next_holiday = h
                break
        if not next_holiday:
            next_holiday = j[0]
        name = next_holiday.get('name', '?')
        date = next_holiday.get('date', '?')
        local_name = next_holiday.get('localName', '')
        lines = [
            f'=== Next Holiday ({display_loc}) ===',
            f'  {name}',
            f'  {date}',
        ]
        if local_name and local_name != name:
            lines.append(f'  ({local_name})')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'holiday: {e}')


def cmd_aqi(args):
    city = args.strip() if args.strip() else 'amsterdam'
    try:
        import ujson
        # Step 1: Geocode the city name to get coordinates
        geo_body = _https_get('geocoding-api.open-meteo.com',
                             f'/v1/search?name={city.replace(" ", "%20")}&count=1',
                             timeout=10)
        geo = ujson.loads(geo_body)
        results = geo.get('results', [])
        if not results:
            return ('print', f'aqi: could not find "{city}"')
        loc = results[0]
        lat = loc.get('latitude')
        lng = loc.get('longitude')
        name = loc.get('name', city)
        country = loc.get('country', '')

        # Step 2: Get AQI data from Open-Meteo
        aqi_body = _https_get('air-quality-api.open-meteo.com',
                              f'/v1/air-quality?latitude={lat}&longitude={lng}'
                              f'&current=us_aqi,pm10,pm2_5,european_aqi',
                              timeout=10)
        aqi_data = ujson.loads(aqi_body)
        current = aqi_data.get('current', {})

        aqi_val = current.get('us_aqi', '?')
        pm25 = current.get('pm2_5', '?')
        pm10 = current.get('pm10', '?')
        eu_aqi = current.get('european_aqi', '?')

        # Determine AQI level (US AQI scale)
        if isinstance(aqi_val, (int, float)):
            if aqi_val <= 50:
                level = 'Good'
            elif aqi_val <= 100:
                level = 'Moderate'
            elif aqi_val <= 150:
                level = 'Unhealthy (sensitive)'
            elif aqi_val <= 200:
                level = 'Unhealthy'
            elif aqi_val <= 300:
                level = 'Very Unhealthy'
            else:
                level = 'Hazardous'
        else:
            level = '?'

        location_str = f'{name}, {country}' if country else name
        lines = [
            f'=== AQI: {location_str} ===',
            f'  US AQI:  {aqi_val} ({level})',
            f'  EU AQI:  {eu_aqi}',
            f'  PM2.5:   {pm25} ug/m3',
            f'  PM10:    {pm10} ug/m3',
        ]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'aqi: {e}')


def cmd_bored(args):
    try:
        import ujson
        body = _https_get('bored-api.appbrewery.com', '/random', timeout=10)
        j = ujson.loads(body)
        activity = j.get('activity', 'No activity found')
        act_type = j.get('type', '?')
        participants = j.get('participants', '?')
        price = j.get('price', 0)
        price_str = 'Free' if price == 0 else f'${price:.1f}'
        lines = [
            '=== Bored? ===',
            '',
            f'  {activity}',
            f'  Type: {act_type}',
            f'  People: {participants}',
            f'  Cost: {price_str}',
        ]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'bored: {e}')


def cmd_forecast(args):
    city = args.strip() if args.strip() else 'Falkensee'
    try:
        import ujson
        geo_body = _https_get('geocoding-api.open-meteo.com',
                             f'/v1/search?name={city.replace(" ", "%20")}&count=1', timeout=10)
        geo = ujson.loads(geo_body)
        results = geo.get('results', [])
        if not results:
            return ('print', f'forecast: could not find "{city}"')
        loc = results[0]
        lat = loc.get('latitude')
        lng = loc.get('longitude')
        name = loc.get('name', city)
        body = _https_get('api.open-meteo.com',
                         f'/v1/forecast?latitude={lat}&longitude={lng}'
                         f'&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode'
                         f'&timezone=auto&forecast_days=5', timeout=10)
        j = ujson.loads(body)
        daily = j.get('daily', {})
        dates = daily.get('time', [])
        maxtemps = daily.get('temperature_2m_max', [])
        mintemps = daily.get('temperature_2m_min', [])
        precip = daily.get('precipitation_sum', [])
        codes = daily.get('weathercode', [])
        wmo = {0: 'Clear', 1: 'Mostly clear', 2: 'Partly cloudy', 3: 'Overcast',
               45: 'Fog', 48: 'Rime fog', 51: 'Light drizzle', 53: 'Drizzle',
               55: 'Dense drizzle', 61: 'Light rain', 63: 'Rain', 65: 'Heavy rain',
               71: 'Light snow', 73: 'Snow', 75: 'Heavy snow', 80: 'Light showers',
               81: 'Showers', 82: 'Heavy showers', 95: 'Thunderstorm'}
        lines = [f'=== Forecast: {name} ===']
        for i in range(min(5, len(dates))):
            code = codes[i] if i < len(codes) else 0
            desc = wmo.get(code, f'Code {code}')
            hi = int(maxtemps[i]) if i < len(maxtemps) else '?'
            lo = int(mintemps[i]) if i < len(mintemps) else '?'
            rain = precip[i] if i < len(precip) else 0
            lines.append('')
            lines.append(f'  {dates[i]}')
            lines.append(f'    {hi}/{lo}C  {desc}')
            if rain > 0:
                lines.append(f'    Rain: {rain}mm')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'forecast: {e}')


def cmd_lyrics(args):
    query = args.strip()
    if not query:
        return ('print', 'numfact: usage: numfact [number]')
    try:
        import ujson
        num = query.replace(' ', '')
        body = _https_get('api.mathjs.org', f'/v4/?expr=eval(pi*{num})', timeout=10)
        result = body.strip()
        lines = [f'=== Number {num} ===', '', f'  pi * {num} = {result}']
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'numfact: {e}')


def cmd_chemical(args):
    try:
        import ujson
        body = _https_get('official-joke-api.appspot.com', '/random_joke', timeout=10)
        j = ujson.loads(body)
        setup = j.get('setup', '')
        punchline = j.get('punchline', '')
        wrapped = _wrap_text(setup, 36)
        lines = ['=== Joke ===', ''] + ['  ' + l for l in wrapped]
        lines.append('')
        pw = _wrap_text(punchline, 36)
        for l in pw:
            lines.append(f'  {l}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'joke2: {e}')


def cmd_catfact(args):
    try:
        import ujson
        body = _https_get('catfact.ninja', '/fact', timeout=10)
        j = ujson.loads(body)
        fact = j.get('fact', 'No fact available')
        wrapped = _wrap_text(fact, 36)
        lines = ['=== Cat Fact ===', ''] + ['  ' + l for l in wrapped]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'catfact: {e}')


def cmd_dogfact(args):
    try:
        import ujson
        body = _https_get('dogfact.ninja', '/fact', timeout=10)
        j = ujson.loads(body)
        fact = j.get('fact', '')
        if not fact:
            body2 = _https_get('dog-api.kinduff.com', '/api/facts', timeout=10)
            j2 = ujson.loads(body2)
            facts = j2.get('facts', [])
            fact = facts[0] if facts else ''
        if not fact:
            return ('print', 'dogfact: no fact available')
        wrapped = _wrap_text(fact, 36)
        lines = ['=== Dog Fact ===', ''] + ['  ' + l for l in wrapped]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'dogfact: {e}')


def cmd_trivia(args):
    try:
        import ujson
        body = _https_get('opentdb.com', '/api.php?amount=1&type=multiple', timeout=10)
        j = ujson.loads(body)
        results = j.get('results', [])
        if not results:
            return ('print', 'trivia: could not fetch question')
        q = results[0]
        question = _wrap_text(q.get('question', '').replace('&quot;', '"').replace('&#039;', "'").replace('&amp;', '&'), 36)
        correct = q.get('correct_answer', '')
        answers = q.get('incorrect_answers', []) + [correct]
        import random
        n = len(answers)
        for i in range(n - 1, 0, -1):
            j = random.randint(0, i)
            answers[i], answers[j] = answers[j], answers[i]
        lines = ['=== Trivia ===', '']
        for l in question:
            lines.append(f'  {l}')
        lines.append('')
        for i, a in enumerate(answers):
            letter = chr(65 + i)
            a_clean = a.replace('&quot;', '"').replace('&#039;', "'").replace('&amp;', '&')
            lines.append(f'  {letter}: {a_clean}')
        lines.append('')
        c_clean = correct.replace('&quot;', '"').replace('&#039;', "'").replace('&amp;', '&')
        lines.append(f'  Answer: {c_clean}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'trivia: {e}')


def cmd_dadjoke(args):
    try:
        import usocket
        import ssl
        sock = usocket.socket()
        sock.settimeout(10)
        addr = usocket.getaddrinfo('icanhazdadjoke.com', 443)[0][-1]
        sock.connect(addr)
        ssock = ssl.wrap_socket(sock, server_hostname='icanhazdadjoke.com')
        req = 'GET / HTTP/1.1\r\nHost: icanhazdadjoke.com\r\nAccept: text/plain\r\nUser-Agent: espelt\r\nConnection: close\r\n\r\n'
        ssock.sendall(req.encode())
        data = b''
        while True:
            try:
                chunk = ssock.read(512)
            except OSError:
                break
            if not chunk:
                break
            data += chunk
        ssock.close()
        raw = data.decode('utf-8', 'ignore')
        header_end = raw.find('\r\n\r\n')
        if header_end >= 0:
            body = raw[header_end + 4:].strip()
        else:
            body = raw
        if body.startswith('{'):
            import ujson
            j = ujson.loads(body)
            body = j.get('joke', body)
        wrapped = _wrap_text(body, 36)
        lines = ['=== Dad Joke ===', ''] + ['  ' + l for l in wrapped]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'dadjoke: {e}')


def cmd_randomfact(args):
    try:
        import ujson
        body = _https_get('uselessfacts.jsph.pl', '/api/v2/facts/random?language=en', timeout=10)
        j = ujson.loads(body)
        fact = j.get('text', 'No fact available')
        wrapped = _wrap_text(fact, 36)
        lines = ['=== Random Fact ===', ''] + ['  ' + l for l in wrapped]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'randomfact: {e}')


def cmd_xkcd(args):
    try:
        import ujson
        body = _https_get('xkcd.com', '/info.0.json', timeout=10)
        j = ujson.loads(body)
        num = j.get('num', '?')
        title = j.get('title', '?')
        alt = j.get('alt', '')
        safe_title = j.get('safe_title', title)
        lines = [
            f'=== XKCD #{num} ===',
            '',
            f'  {safe_title}',
            '',
        ]
        for l in _wrap_text(alt, 36):
            lines.append(f'  {l}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'xkcd: {e}')


def cmd_vocab(args):
    try:
        import ujson
        body = _https_get('random-word-api.herokuapp.com', '/word?number=1', timeout=10)
        j = ujson.loads(body)
        word = j[0] if isinstance(j, list) and len(j) > 0 else None
        if not word:
            return ('print', 'vocab: could not fetch word')
        def_body = _https_get('api.dictionaryapi.dev', f'/api/v2/entries/en/{word}', timeout=10)
        dj = ujson.loads(def_body)
        lines = [f'=== Word of the Day ===', '', f'  {word}']
        if isinstance(dj, list) and len(dj) > 0:
            entry = dj[0]
            phonetic = entry.get('phonetic', '')
            if phonetic:
                lines.append(f'  {phonetic}')
            meanings = entry.get('meanings', [])
            if meanings:
                primary = meanings[0]
                pos = primary.get('partOfSpeech', '')
                defs = primary.get('definitions', [])
                if defs:
                    d = defs[0].get('definition', '')
                    wrapped = _wrap_text(d, 36)
                    lines.append(f'  [{pos}]')
                    for l in wrapped:
                        lines.append(f'    {l}')
                    ex = defs[0].get('example', '')
                    if ex:
                        ex_wrapped = _wrap_text(f'"{ex}"', 34)
                        lines.append(f'  e.g.')
                        for l in ex_wrapped:
                            lines.append(f'    {l}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'vocab: {e}')


def cmd_geo(args):
    try:
        import usocket
        import ujson
        sock = usocket.socket()
        sock.settimeout(10)
        addr = usocket.getaddrinfo('ip-api.com', 80)[0][-1]
        sock.connect(addr)
        sock.sendall(b'GET /json/ HTTP/1.1\r\nHost: ip-api.com\r\nConnection: close\r\n\r\n')
        data = b''
        while True:
            try:
                chunk = sock.read(1024)
            except:
                break
            if not chunk:
                break
            data += chunk
        sock.close()
        raw = data.decode('utf-8', 'ignore')
        idx = raw.find('\r\n\r\n')
        body = raw[idx+4:].lstrip('\r\n') if idx >= 0 else raw
        j = ujson.loads(body)
        if j.get('status') == 'fail':
            return ('print', 'geo: could not determine location')
        lat = j.get('lat', 0)
        lon = j.get('lon', 0)
        city = j.get('city', '?')
        region = j.get('regionName', '?')
        country = j.get('country', '?')
        isp = j.get('isp', '?')
        lines = [
            f'=== Location ===',
            f'  {city}, {region}',
            f'  {country}',
            f'  Lat: {lat}',
            f'  Lon: {lon}',
            f'  ISP: {isp}',
        ]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'geo: {e}')


def cmd_npm(args):
    package = args.strip()
    if not package:
        return ('print', 'npm: usage: npm [package name]')
    try:
        import ujson
        body = _https_get('registry.npmjs.org', f'/{package}', timeout=10)
        j = ujson.loads(body)
        name = j.get('name', package)
        desc = j.get('description', 'No description')
        latest = j.get('dist-tags', {}).get('latest', '?')
        versions = j.get('versions', {})
        author = j.get('author', {})
        author_name = author.get('name', '?') if isinstance(author, dict) else str(author)
        lines = [
            f'=== {name} v{latest} ===',
            '',
        ]
        for l in _wrap_text(desc, 36):
            lines.append(f'  {l}')
        lines.append(f'  Author: {author_name}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'npm: {e}')


def cmd_pypi(args):
    package = args.strip()
    if not package:
        return ('print', 'pypi: usage: pypi [package name]')
    try:
        import ujson
        body = _https_get('pypi.org', f'/pypi/{package}/json', timeout=10)
        j = ujson.loads(body)
        info = j.get('info', {})
        name = info.get('name', package)
        version = info.get('version', '?')
        summary = info.get('summary', 'No summary')
        author = info.get('author', '') or info.get('author_email', '?')
        home = info.get('home_page', '') or info.get('project_url', '')
        lines = [
            f'=== {name} v{version} ===',
            '',
        ]
        for l in _wrap_text(summary, 36):
            lines.append(f'  {l}')
        lines.append(f'  Author: {author[:30]}')
        if home:
            lines.append(f'  URL: {home[:36]}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'pypi: {e}')


def cmd_convert(args):
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 3:
        return ('print_lines', [
            'convert: usage: convert [val] [from] [to]',
            '',
            '  km mi, kg lb, C F, l gal',
            '  m ft, cm in, km/h mph',
        ])
    try:
        val = float(parts[0])
        fr = parts[1].lower()
        to = parts[2].lower()
        conversions = {
            ('km', 'mi'): 0.621371, ('mi', 'km'): 1.60934,
            ('kg', 'lb'): 2.20462, ('lb', 'kg'): 0.453592,
            ('c', 'f'): lambda x: x * 9 / 5 + 32,
            ('f', 'c'): lambda x: (x - 32) * 5 / 9,
            ('l', 'gal'): 0.264172, ('gal', 'l'): 3.78541,
            ('m', 'ft'): 3.28084, ('ft', 'm'): 0.3048,
            ('cm', 'in'): 0.393701, ('in', 'cm'): 2.54,
            ('km/h', 'mph'): 0.621371, ('mph', 'km/h'): 1.60934,
        }
        key = (fr, to)
        if key not in conversions:
            return ('print', f'convert: unknown conversion {fr} -> {to}')
        conv = conversions[key]
        result = conv(val) if callable(conv) else val * conv
        return ('print_lines', [
            f'=== Convert ===',
            f'  {val} {fr} = {result:.2f} {to}',
        ])
    except ValueError:
        return ('print', 'convert: invalid number')
    except Exception as e:
        return ('print', f'convert: {e}')


def cmd_quote(args):
    try:
        import ujson
        body = _https_get('zenquotes.io', '/api/random', timeout=10)
        j = ujson.loads(body)
        if isinstance(j, list) and len(j) > 0:
            text = j[0].get('q', 'No quote available')
            author = j[0].get('a', '?')
        else:
            return ('print', 'quote: could not fetch quote')
        wrapped = _wrap_text(text, 36)
        lines = ['=== Quote ===', ''] + ['  ' + l for l in wrapped]
        lines.append(f'  - {author}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'quote: {e}')


def cmd_roast(args):
    try:
        import ujson
        body = _https_get('api.chucknorris.io', '/jokes/random', timeout=10)
        j = ujson.loads(body)
        text = j.get('value', 'No roast available')
        wrapped = _wrap_text(text, 36)
        lines = ['=== Roast ===', ''] + ['  ' + l for l in wrapped]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'roast: {e}')


def cmd_ghrepofs(args):
    repo = args.strip()
    if not repo:
        return ('print', 'ghrepofs: usage: ghrepofs [user/repo] [path]')
    parts = repo.split()
    repo_name = parts[0]
    subpath = parts[1] if len(parts) > 1 else ''
    try:
        import ujson
        if subpath:
            path = f'/repos/{repo_name}/contents/{subpath}'
        else:
            path = f'/repos/{repo_name}/contents'
        body = _https_get('api.github.com', path, timeout=15)
        j = ujson.loads(body)
        if isinstance(j, dict) and 'message' in j:
            return ('print', f'ghrepofs: {j["message"]}')
        if not isinstance(j, list):
            return ('print', 'ghrepofs: unexpected response')
        lines = [f'=== {repo_name}/{subpath} ===' if subpath else f'=== {repo_name} ===']
        lines.append('')
        dirs = []
        files = []
        for item in j:
            name = item.get('name', '?')
            item_type = item.get('type', '?')
            size = item.get('size', 0)
            if item_type == 'dir':
                dirs.append(f'  {name}/')
            else:
                size_str = ''
                if size > 1024:
                    size_str = f' ({size // 1024}KB)'
                elif size > 0:
                    size_str = f' ({size}B)'
                files.append(f'  {name}{size_str}')
        for d in sorted(dirs):
            lines.append(d)
        for f in sorted(files):
            lines.append(f)
        if not dirs and not files:
            lines.append('  (empty)')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'ghrepofs: {e}')


def _parse_rss(xml_text):
    articles = []
    # Find <item>...</item> or <entry>...</entry> blocks manually
    items = []
    for tag in ['item', 'entry']:
        start_tag = '<' + tag + '>'
        end_tag = '</' + tag + '>'
        pos = 0
        while True:
            idx = xml_text.find(start_tag, pos)
            if idx < 0:
                break
            end_idx = xml_text.find(end_tag, idx)
            if end_idx < 0:
                break
            items.append(xml_text[idx + len(start_tag):end_idx])
            pos = end_idx + len(end_tag)

    for item in items:
        title = _xml_find(item, 'title')
        link = _xml_find(item, 'link')
        desc = _xml_find(item, 'description') or _xml_find(item, 'summary') or _xml_find(item, 'content')
        title_text = title if title else 'No title'
        link_text = link if link else ''
        desc_text = desc if desc else ''
        # Strip HTML tags
        while True:
            lt = desc_text.find('<')
            if lt < 0:
                break
            gt = desc_text.find('>', lt)
            if gt < 0:
                break
            desc_text = desc_text[:lt] + desc_text[gt + 1:]
        desc_text = desc_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        desc_text = desc_text.replace('&#39;', "'").replace('&quot;', '"')
        # Strip HTML from title too
        while True:
            lt = title_text.find('<')
            if lt < 0:
                break
            gt = title_text.find('>', lt)
            if gt < 0:
                break
            title_text = title_text[:lt] + title_text[gt + 1:]
        articles.append({
            'title': title_text[:60],
            'link': link_text,
            'description': desc_text[:200],
        })
    return articles


def _xml_find(text, tag):
    start = '<' + tag + '>'
    idx = text.find(start)
    if idx < 0:
        return None
    end = '</' + tag + '>'
    end_idx = text.find(end, idx)
    if end_idx < 0:
        return None
    return text[idx + len(start):end_idx]


RSS_FEEDS = {
    'hn': ('Hacker News', 'hnrss.org', '/newest?points=100&count=10'),
    'hackernews': ('Hacker News', 'hnrss.org', '/newest?points=100&count=10'),
    'lobste': ('Lobsters', 'lobste.rs', '/rss'),
    'lobsters': ('Lobsters', 'lobste.rs', '/rss'),
    'reddit': ('Reddit /r/programming', 'www.reddit.com', '/r/programming/.rss'),
    'bbc': ('BBC News', 'feeds.bbci.co.uk', '/news/rss.xml'),
    'techcrunch': ('TechCrunch', 'techcrunch.com', '/feed/'),
}


def cmd_rss(args, tft=None):
    feed_arg = args.strip().lower()
    if not feed_arg:
        lines = ['=== RSS Feeds ===', '']
        for name, (label, host, path) in RSS_FEEDS.items():
            lines.append(f'  {name:14s} {label}')
        lines.append('')
        lines.append('Usage: rss [feed|url]')
        lines.append('  rss hn     Hacker News')
        lines.append('  rss bbc    BBC News')
        lines.append('  rss <url>  Custom feed URL')
        return ('print_lines', lines)

    feed_name = feed_arg
    if feed_arg in RSS_FEEDS:
        label, host, path = RSS_FEEDS[feed_arg]
        feed_name = label
        use_https = True
    else:
        url = args.strip()
        if '://' in url:
            scheme_end = url.find('://')
            scheme = url[:scheme_end]
            rest = url[scheme_end + 3:]
            slash = rest.find('/')
            if slash < 0:
                host = rest
                path = '/'
            else:
                host = rest[:slash]
                path = rest[slash:]
            use_https = scheme == 'https'
            label = host
        else:
            return ('print', 'rss: usage: rss [hn|lobste|reddit|bbc|techcrunch|url]')
        feed_name = label

    try:
        if use_https:
            body = _https_get(host, path, timeout=15)
        else:
            body = _http_get(host, path, timeout=15)
        articles = _parse_rss(body)
        if not articles:
            return ('print', f'rss: no articles found in {feed_name}')

        def _rss_loop(tft, read_key):
            import time
            from commands.dispatch import THEME_COLORS
            sel = 0
            scroll = 0
            showing_detail = False

            if THEME_COLORS:
                _bg = THEME_COLORS['bg']
                _fg = THEME_COLORS['white']
                _accent = THEME_COLORS['accent']
                _green = THEME_COLORS['green']
                _yellow = THEME_COLORS['yellow']
                _header = THEME_COLORS['header']
            else:
                _bg = 0x0000
                _fg = 0xFFFF
                _accent = 0x07FF
                _green = 0x07E0
                _yellow = 0xFFE0
                _header = 0x1082

            def _render_list():
                tft.fill(_bg)
                header = 'RSS: ' + feed_name
                tft.text15(header[:36], 4, 2, _accent, _bg)
                visible = 14
                total = len(articles)
                max_scroll = max(0, total - visible)
                if scroll > max_scroll:
                    scroll = max_scroll
                for i in range(visible):
                    idx = i + scroll
                    y = 20 + i * 16
                    if idx >= total:
                        break
                    a = articles[idx]
                    prefix = chr(0x96) + ' '
                    color = _fg
                    if idx == sel:
                        tft.fill_rect(0, y, 480, 16, _accent)
                        color = _fg
                    tft.text15(prefix + a['title'][:42], 4, y, color, _bg if idx != sel else _accent)
                if total == 0:
                    tft.text15('  No articles found.', 4, 36, _yellow, _bg)
                help_y = 306
                tft.text15('Up/Down:Scroll  Enter:Detail  Q:Quit', 4, help_y, _accent, _bg)
                tft.text15(f'{sel + 1}/{total}', 430, help_y, _green, _bg)

            def _render_detail():
                tft.fill(_bg)
                a = articles[sel]
                header = f'=== {sel + 1}/{len(articles)} ==='
                tft.text15(header[:36], 4, 2, _accent, _bg)
                tft.text15(a['title'][:36], 4, 20, _yellow, _bg)
                desc = a['description']
                if not desc:
                    desc = '(no description)'
                lines = []
                words = desc.split()
                line = ''
                for w in words:
                    test = (line + ' ' + w).strip() if line else w
                    if len(test) <= 36:
                        line = test
                    else:
                        if line:
                            lines.append(line)
                        line = w
                if line:
                    lines.append(line)
                y = 40
                for l in lines[:15]:
                    tft.text15(l, 4, y, _fg, _bg)
                    y += 16
                help_y = 306
                tft.text15('Esc/Q:Back  Up/Down:Prev/Next', 4, help_y, _accent, _bg)

            _render_list()

            while True:
                ch = read_key()

                if showing_detail:
                    if ch == '\x1b' or ch == 'q' or ch == 'Q':
                        showing_detail = False
                        _render_list()
                    elif ch == '\x80':
                        if sel > 0:
                            sel -= 1
                            scroll = max(0, min(sel, scroll))
                        _render_detail()
                    elif ch == '\x81':
                        if sel < len(articles) - 1:
                            sel += 1
                            if sel >= scroll + 14:
                                scroll = sel - 13
                        _render_detail()
                else:
                    if ch == '\x1b' or ch == 'q' or ch == 'Q':
                        tft.fill(_bg)
                        tft.text15('Exiting RSS...', 4, 150, _green, _bg)
                        time.sleep_ms(300)
                        return

                    if ch == '\n':
                        showing_detail = True
                        _render_detail()

                    elif ch == '\x80':
                        if sel > 0:
                            sel -= 1
                            if sel < scroll:
                                scroll = sel
                        _render_list()

                    elif ch == '\x81':
                        if sel < len(articles) - 1:
                            sel += 1
                            if sel >= scroll + 14:
                                scroll = sel - 13
                        _render_list()

        return ('game', _rss_loop)
    except Exception as e:
        return ('print', f'rss: {e}')


def cmd_chuck(args):
    try:
        import ujson
        body = _https_get('api.chucknorris.io', '/jokes/random', timeout=10)
        j = ujson.loads(body)
        joke = j.get('value', 'No joke available')
        wrapped = _wrap_text(joke, 36)
        lines = ['=== Chuck Norris ===', ''] + ['  ' + l for l in wrapped]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'chuck: {e}')


def cmd_earthquake(args):
    try:
        import ujson
        parts = args.strip().split() if args.strip() else []
        count = 5
        if parts and parts[0].isdigit():
            count = min(int(parts[0]), 10)
        body = _https_get('earthquake.usgs.gov',
                          '/earthquakes/feed/v1.0/summary/significant_week.geojson',
                          timeout=10)
        j = ujson.loads(body)
        features = j.get('features', [])
        if not features:
            return ('print', 'earthquake: no significant quakes this week')
        lines = [f'=== Earthquakes ({count}) ===', '']
        for i, feat in enumerate(features[:count]):
            props = feat.get('properties', {})
            mag = props.get('mag', '?')
            place = props.get('place', 'Unknown')
            ts = props.get('time', 0)
            if ts:
                secs = ts // 1000
                mins = secs // 60
                hrs = mins // 60
                day = hrs // 24
                hrs = hrs % 24
                mins = mins % 60
                time_str = f'{day}d{hrs}h{mins}m ago'
            else:
                time_str = '?'
            mag_str = str(mag) if isinstance(mag, (int, float)) else mag
            loc_lines = _wrap_text(place, 30)
            lines.append(f'  M{mag_str} - {loc_lines[0]}')
            for ll in loc_lines[1:]:
                lines.append(f'    {ll}')
            lines.append(f'    {time_str}')
            if i < len(features[:count]) - 1:
                lines.append('')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'earthquake: {e}')


def cmd_colorinfo(args):
    hex_str = args.strip().lstrip('#').upper()
    if not hex_str or len(hex_str) not in (3, 6):
        return ('print_lines', [
            'colorinfo: usage: colorinfo [hex]',
            '',
            '  Example: colorinfo FF0000',
            '  Example: colorinfo F00',
        ])

    if len(hex_str) == 3:
        hex_str = hex_str[0]*2 + hex_str[1]*2 + hex_str[2]*2

    try:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
    except ValueError:
        return ('print', 'colorinfo: invalid hex color')

    comp_r = 255 - r
    comp_g = 255 - g
    comp_b = 255 - b
    comp_hex = f'{comp_r:02X}{comp_g:02X}{comp_b:02X}'

    def _clamp(v):
        return max(0, min(255, v))

    an1_r = _clamp(r + 30)
    an1_g = _clamp(g - 15)
    an1_b = _clamp(b - 15)
    an2_r = _clamp(r - 15)
    an2_g = _clamp(g + 30)
    an2_b = _clamp(b - 15)
    an1_hex = f'{an1_r:02X}{an1_g:02X}{an1_b:02X}'
    an2_hex = f'{an2_r:02X}{an2_g:02X}{an2_b:02X}'

    named_colors = {
        'FF0000': 'Red', '00FF00': 'Green', '0000FF': 'Blue',
        'FFFF00': 'Yellow', 'FF00FF': 'Magenta', '00FFFF': 'Cyan',
        'FFFFFF': 'White', '000000': 'Black', 'FF8000': 'Orange',
        '800080': 'Purple', 'FFC0CB': 'Pink', '808080': 'Gray',
        '800000': 'Maroon', '008000': 'Dark Green', '000080': 'Navy',
        'FFD700': 'Gold', 'C0C0C0': 'Silver', 'A52A2A': 'Brown',
        'FF6347': 'Tomato', '4682B4': 'Steel Blue', '2E8B57': 'Sea Green',
        'FF1493': 'Deep Pink', '1E90FF': 'Dodger Blue', '32CD32': 'Lime Green',
        'FA8072': 'Salmon', 'DDA0DD': 'Plum', '90EE90': 'Light Green',
    }

    closest = 'Custom'
    min_dist = 999999
    for hc, nm in named_colors.items():
        hr = int(hc[0:2], 16)
        hg = int(hc[2:4], 16)
        hb = int(hc[4:6], 16)
        dist = (r - hr) ** 2 + (g - hg) ** 2 + (b - hb) ** 2
        if dist < min_dist:
            min_dist = dist
            closest = nm

    lines = [
        f'=== Color #{hex_str} ===',
        '',
        f'  Name: {closest}',
        f'  RGB:  ({r}, {g}, {b})',
        '',
        f'  Complement:',
        f'  #{comp_hex} ({comp_r},{comp_g},{comp_b})',
        '',
        f'  Analogous:',
        f'  #{an1_hex}',
        f'  #{an2_hex}',
    ]
    return ('print_lines', lines)


def cmd_nasa_apod(args):
    try:
        import ujson
        body = _https_get('api.nasa.gov',
                          '/planetary/apod?api_key=DEMO_KEY',
                          timeout=10)
        j = ujson.loads(body)
        title = j.get('title', 'No title')
        explanation = j.get('explanation', 'No explanation')
        date = j.get('date', '?')
        media = j.get('media_type', '?')
        wrapped = _wrap_text(explanation, 36)
        lines = [
            f'=== NASA APOD ===',
            '',
            f'  {title}',
            f'  Date: {date}',
            f'  Type: {media}',
            '',
        ] + ['  ' + l for l in wrapped[:8]]
        if len(wrapped) > 8:
            lines.append('  ...')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'nasa_apod: {e}')


def cmd_sunset(args):
    """Sunrise/sunset times via sunrise-sunset.org API."""
    try:
        import ujson
        lat = '52.39'
        lon = '13.06'
        city = 'Falkensee'
        if args.strip():
            parts = args.strip().split()
            if len(parts) >= 2:
                lat, lon = parts[0], parts[1]
                city = f'{lat},{lon}'
            elif len(parts) == 1:
                city = parts[0]
                city_coords = {
                    'berlin': ('52.52', '13.41'),
                    'london': ('51.51', '-0.13'),
                    'paris': ('48.86', '2.35'),
                    'newyork': ('40.71', '-74.01'),
                    'tokyo': ('35.68', '139.69'),
                    'falkensee': ('52.39', '13.06'),
                }
                if city.lower() in city_coords:
                    lat, lon = city_coords[city.lower()]
        body = _http_get('api.sunrise-sunset.org',
                        f'/json?lat={lat}&lng={lon}&formatted=0',
                        timeout=10)
        j = ujson.loads(body)
        results = j.get('results', {})
        sunrise = results.get('sunrise', '?')
        sunset = results.get('sunset', '?')
        dawn = results.get('civl_twilight_begin', '?')
        dusk = results.get('civl_twilight_end', '?')
        day_len = results.get('day_length', '?')
        lines = [
            f'=== Sunset/Sunrise ===',
            f'  Location: {city}',
            f'  Sunrise:  {sunrise[11:19] if len(sunrise) > 11 else sunrise}',
            f'  Sunset:   {sunset[11:19] if len(sunset) > 11 else sunset}',
            f'  Dawn:     {dawn[11:19] if len(dawn) > 11 else dawn}',
            f'  Dusk:     {dusk[11:19] if len(dusk) > 11 else dusk}',
        ]
        if isinstance(day_len, (int, float)):
            hrs = int(day_len) // 3600
            mins = (int(day_len) % 3600) // 60
            lines.append(f'  Day len:  {hrs}h {mins}m')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'sunset: {e}')


def cmd_randomuser(args):
    """Random user profile via randomuser.me API."""
    try:
        import ujson
        body = _http_get('randomuser.me', '/api/', timeout=10)
        j = ujson.loads(body)
        u = j['results'][0]
        name = f'{u["name"]["first"]} {u["name"]["last"]}'
        loc = f'{u["location"]["city"]}, {u["location"]["country"]}'
        email = u.get('email', '?')
        age = u.get('dob', {}).get('age', '?')
        phone = u.get('phone', '?')
        lines = [
            f'=== Random User ===',
            f'  Name:   {name}',
            f'  Age:    {age}',
            f'  Email:  {email}',
            f'  Phone:  {phone}',
            f'  From:   {loc}',
        ]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'randomuser: {e}')


def cmd_ipwhois(args):
    """IP WHOIS lookup via ipwho.is."""
    try:
        import ujson
        ip = args.strip() if args.strip() else ''
        path = f'/{ip}' if ip else '/'
        body = _http_get('ipwho.is', path, timeout=10)
        j = ujson.loads(body)
        if not j.get('success', False):
            return ('print', f'ipwhois: {j.get("message", "lookup failed")}')
        ip_addr = j.get('ip', '?')
        city = j.get('city', '?')
        region = j.get('region', '?')
        country = j.get('country', '?')
        org = j.get('org', '?')
        lat = j.get('latitude', '?')
        lon = j.get('longitude', '?')
        lines = [
            f'=== IP Info ===',
            f'  IP:      {ip_addr}',
            f'  City:    {city}',
            f'  Region:  {region}',
            f'  Country: {country}',
            f'  Org:     {org}',
            f'  Coords:  {lat}, {lon}',
        ]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'ipwhois: {e}')


def cmd_color(args):
    """Generate random color palette."""
    import random
    count = 5
    if args.strip():
        try:
            count = min(int(args.strip()), 12)
        except ValueError:
            pass
    lines = ['=== Color Palette ===']
    for _ in range(count):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        hex_c = f'#{r:02X}{g:02X}{b:02X}'
        lines.append(f'  {hex_c}  RGB({r},{g},{b})')
    return ('print_lines', lines)


def cmd_uptime_api(args):
    """Public server uptime check."""
    try:
        import ujson
        sites = {
            'google': ('www.google.com', '/'),
            'github': ('github.com', '/'),
            'cloudflare': ('1.1.1.1', '/cdn-cgi/trace'),
            'wikipedia': ('en.wikipedia.org', '/'),
        }
        name = args.strip().lower() if args.strip() else 'google'
        if name not in sites:
            return ('print_lines', [
                f'Available: {", ".join(sites.keys())}',
            ])
        host, path = sites[name]
        import time
        t0 = time.ticks_ms()
        body = _http_get(host, path, timeout=5)
        t1 = time.ticks_ms()
        ms = time.ticks_diff(t1, t0)
        status = 'UP' if body else 'DOWN'
        lines = [
            f'=== Uptime Check ===',
            f'  Site:   {name}',
            f'  Status: {status}',
            f'  Time:   {ms}ms',
        ]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'uptime: {e}')


def cmd_json(args):
    """JSON pretty-print / parse."""
    if not args.strip():
        return ('print', 'Usage: json <json_string>')
    try:
        import ujson
        data = ujson.loads(args.strip())
        lines = ['=== JSON ===']
        _json_pretty(data, lines, indent=0)
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'json: {e}')


def _json_pretty(data, lines, indent=0):
    pad = '  ' * (indent + 1)
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f'{pad}{k}:')
                _json_pretty(v, lines, indent + 1)
            else:
                lines.append(f'{pad}{k}: {v}')
    elif isinstance(data, list):
        for i, v in enumerate(data):
            if isinstance(v, (dict, list)):
                lines.append(f'{pad}[{i}]:')
                _json_pretty(v, lines, indent + 1)
            else:
                lines.append(f'{pad}{v}')
    else:
        lines.append(f'{pad}{data}')


def cmd_wolfram(args):
    """Wolfram Alpha short answers via API."""
    if not args.strip():
        return ('print', 'Usage: wolfram <query>')
    try:
        import ujson
        q = args.strip().replace(' ', '%20')
        body = _http_get('api.wolframalpha.com',
                        f'/v1/result?i={q}&appid=DEMO_KEY',
                        timeout=15)
        lines = [
            f'=== Wolfram Alpha ===',
            f'  Q: {args.strip()[:36]}',
            f'  A: {body.strip()[:36]}',
        ]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'wolfram: {e}')


def cmd_zen(args):
    """Random zen quote from GitHub Zen API."""
    try:
        body = _http_get('api.github.com', '/zen', timeout=10)
        lines = ['=== GitHub Zen ===', f'  {body.strip()}']
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'zen: {e}')


def cmd_books(args):
    """Book search via Open Library API."""
    if not args.strip():
        return ('print', 'Usage: books <title or author>')
    try:
        import ujson
        q = args.strip().replace(' ', '%20')
        body = _http_get('openlibrary.org',
                        f'/search.json?q={q}&limit=3', timeout=10)
        j = ujson.loads(body)
        docs = j.get('docs', [])
        if not docs:
            return ('print', f'books: no results for "{args.strip()}"')
        lines = ['=== Books ===']
        for d in docs:
            title = d.get('title', '?')
            author = ', '.join(d.get('author_name', ['?'])[:2])
            year = d.get('first_publish_year', '?')
            lines.append(f'  {title}')
            lines.append(f'  by {author} ({year})')
            lines.append('')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'books: {e}')


def cmd_movies(args):
    """Movie search via OMDb API (free tier)."""
    if not args.strip():
        return ('print', 'Usage: movies <title>')
    try:
        import ujson
        q = args.strip().replace(' ', '%20')
        body = _http_get('www.omdbapi.com',
                        f'/?t={q}&apikey=trilogy', timeout=10)
        j = ujson.loads(body)
        if j.get('Response') == 'False':
            return ('print', f'movies: {j.get("Error", "not found")}')
        title = j.get('Title', '?')
        year = j.get('Year', '?')
        rated = j.get('Rated', '?')
        rating = j.get('imdbRating', '?')
        genre = j.get('Genre', '?')
        plot = j.get('Plot', '?')
        wrapped = _wrap_text(plot, 36)
        lines = [
            f'=== Movie ===',
            f'  {title} ({year})',
            f'  Rating:  {rating} ({rated})',
            f'  Genre:   {genre}',
            '',
        ] + ['  ' + l for l in wrapped[:4]]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'movies: {e}')


def cmd_iplookup(args):
    """IP geolocation via ip-api.com."""
    ip = args.strip() if args.strip() else ''
    try:
        import ujson
        path = f'/json/{ip}' if ip else '/json/'
        body = _http_get('ip-api.com', path, timeout=10)
        j = ujson.loads(body)
        if j.get('status') == 'fail':
            return ('print', f'iplookup: {j.get("message", "failed")}')
        lines = [
            f'=== IP Lookup ===',
            f'  IP:      {j.get("query", "?")}',
            f'  City:    {j.get("city", "?")}',
            f'  Region:  {j.get("regionName", "?")}',
            f'  Country: {j.get("country", "?")}',
            f'  ISP:     {j.get("isp", "?")}',
            f'  Org:     {j.get("org", "?")}',
        ]
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'iplookup: {e}')


def cmd_whoami(args):
    """Who am I? Random identity generator."""
    import random
    first = ['Alex', 'Jordan', 'Sam', 'Casey', 'Morgan', 'Riley', 'Quinn', 'Avery']
    last = ['Smith', 'Chen', 'Patel', 'Kim', 'Mueller', 'Silva', 'Tanaka', 'Ali']
    cities = ['Berlin', 'Tokyo', 'New York', 'London', 'Sao Paulo', 'Mumbai', 'Sydney']
    hobbies = ['coding', 'gaming', 'reading', 'hiking', 'cooking', 'photography', 'music']
    name = f'{random.choice(first)} {random.choice(last)}'
    city = random.choice(cities)
    hobby = random.choice(hobbies)
    lines = [
        f'=== Who Am I? ===',
        f'  Name:  {name}',
        f'  From:  {city}',
        f'  Hobby: {hobby}',
    ]
    return ('print_lines', lines)


def cmd_ytchl(args):
    """YouTube channel info via internal API + RSS feed."""
    if not args.strip():
        return ('print', 'Usage: ytchl <channel_name>')
    try:
        query = args.strip().replace(' ', '+')
        # Step 1: search via YouTube internal API (tiny JSON, not MB of HTML)
        payload = '{{"query":"{}","context":{{"client":{{"clientName":"MWEB","clientVersion":"2.20240101.00.00"}}}}}}'.format(query)
        body = _https_post('www.youtube.com',
                           '/youtubei/v1/search?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
                           payload, timeout=10)
        # Find channelId in response (may have space after colon)
        ch_id = None
        idx = body.find('"channelId":')
        if idx >= 0:
            start = idx + 12
            # skip space if present
            if start < len(body) and body[start] == ' ':
                start += 1
            # skip opening quote
            if start < len(body) and body[start] == '"':
                start += 1
            end = body.find('"', start)
            if end > start:
                ch_id = body[start:end]
        if not ch_id:
            return ('print', 'ytchl: channel not found')

        # Step 2: get RSS feed for channel name + recent videos
        rss = _https_get('www.youtube.com',
                         '/feeds/videos.xml?channel_id=' + ch_id,
                         timeout=10)

        # Parse title
        title_start = rss.find('<title>')
        title_end = rss.find('</title>', title_start)
        name = rss[title_start + 7:title_end] if title_start >= 0 else '?'
        for ent, ch in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                        ('&quot;', '"'), ('&#39;', "'")]:
            name = name.replace(ent, ch)

        # Parse recent videos
        videos = []
        pos = 0
        for _ in range(5):
            vs = rss.find('<title>', pos)
            if vs < 0:
                break
            ve = rss.find('</title>', vs)
            if ve < 0:
                break
            vtitle = rss[vs + 7:ve]
            for ent, ch in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                            ('&quot;', '"'), ('&#39;', "'")]:
                vtitle = vtitle.replace(ent, ch)
            if vtitle != name:
                videos.append(vtitle)
            pos = ve + 8

        lines = [f'=== {name} ===']
        lines.append(f'  youtube.com/channel/{ch_id}')
        if videos:
            lines.append('')
            lines.append('  Recent videos:')
            for v in videos:
                lines.append(f'    - {v[:40]}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'ytchl: {e}')


def cmd_ytdt(args):
    """YouTube channel detailed stats via internal API."""
    if not args.strip():
        return ('print', 'Usage: ytdt <channel_name>')
    try:
        import ujson
        query = args.strip().replace(' ', '+')
        # Step 1: search for channel ID (MWEB = ~35KB)
        payload = '{{"query":"{}","context":{{"client":{{"clientName":"MWEB","clientVersion":"2.20240101.00.00"}}}}}}'.format(query)
        body = _https_post('www.youtube.com',
                           '/youtubei/v1/search?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
                           payload, timeout=10)
        ch_id = None
        idx = body.find('"channelId":')
        if idx >= 0:
            start = idx + 12
            if start < len(body) and body[start] == ' ':
                start += 1
            if start < len(body) and body[start] == '"':
                start += 1
            end = body.find('"', start)
            if end > start:
                ch_id = body[start:end]
        if not ch_id:
            return ('print', 'ytdt: channel not found')

        # Step 2: browse channel for stats
        payload2 = '{{"browseId":"{}","context":{{"client":{{"clientName":"MWEB","clientVersion":"2.20240101.00.00"}}}}}}'.format(ch_id)
        body2 = _https_post('www.youtube.com',
                            '/youtubei/v1/browse?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
                            payload2, timeout=10)
        data = ujson.loads(body2)

        # Parse metadataRows
        phr = data.get('header', {}).get('pageHeaderRenderer', {})
        vm = phr.get('content', {}).get('pageHeaderViewModel', {})
        meta = vm.get('metadata', {}).get('contentMetadataViewModel', {})
        rows = meta.get('metadataRows', [])

        handle = '?'
        subs = '?'
        vid_count = '?'

        # Row 0: handle, pronouns
        if len(rows) > 0:
            parts = rows[0].get('metadataParts', [])
            if parts:
                handle = parts[0].get('text', {}).get('content', '?')

        # Row 1: subscribers, videos
        if len(rows) > 1:
            parts = rows[1].get('metadataParts', [])
            if len(parts) > 0:
                subs = parts[0].get('text', {}).get('content', '?')
            if len(parts) > 1:
                vid_count = parts[1].get('text', {}).get('content', '?')

        # Get channel name from title
        name = handle
        title_data = vm.get('title', {})
        name = title_data.get('dynamicTextViewModel', {}).get('text', {}).get('content', name)
        if name == handle:
            name = title_data.get('text', {}).get('content', name)

        # Get description
        desc_data = vm.get('description', {})
        description = desc_data.get('descriptionPreviewViewModel', {}).get('description', {}).get('content', '')
        if not description:
            description = desc_data.get('text', {}).get('content', '')

        # Get recent videos from RSS
        rss = _https_get('www.youtube.com',
                         '/feeds/videos.xml?channel_id=' + ch_id,
                         timeout=10)
        videos = []
        pos = 0
        for _ in range(5):
            vs = rss.find('<title>', pos)
            if vs < 0:
                break
            ve = rss.find('</title>', vs)
            if ve < 0:
                break
            vtitle = rss[vs + 7:ve]
            for ent, ch in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                            ('&quot;', '"'), ('&#39;', "'")]:
                vtitle = vtitle.replace(ent, ch)
            if vtitle != name:
                videos.append(vtitle)
            pos = ve + 8

        lines = [f'=== {name} ===']
        lines.append(f'  @{handle.lstrip("@")}')
        lines.append(f'  Subs:    {subs}')
        lines.append(f'  Videos:  {vid_count}')
        if description:
            lines.append(f'  About:   {description[:80]}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'ytdt: {e}')


def cmd_reddit(args):
    """Reddit top posts from a subreddit."""
    if not args.strip():
        return ('print', 'Usage: reddit <subreddit>')
    sub = args.strip().lower().replace('r/', '')
    try:
        import ujson
        body = _https_get('www.reddit.com', f'/r/{sub}/hot.json?limit=8', timeout=10)
        data = ujson.loads(body)
        posts = data.get('data', {}).get('children', [])
        if not posts:
            return ('print', f'reddit: no posts in r/{sub}')
        lines = [f'=== r/{sub} ===']
        for p in posts[:8]:
            d = p.get('data', {})
            title = d.get('title', '?')[:40]
            ups = d.get('ups', 0)
            comments = d.get('num_comments', 0)
            lines.append(f'  [{ups}|{comments}] {title}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'reddit: {e}')


def cmd_ytsearch(args):
    """YouTube search via Invidious API."""
    if not args.strip():
        return ('print', 'Usage: ytsearch <query>')
    try:
        import ujson
        query = args.strip().replace(' ', '+')
        body = _https_get('inv.nadeko.net', f'/api/v1/search?q={query}&type=video', timeout=10)
        results = ujson.loads(body)
        if not results:
            return ('print', 'ytsearch: no results')
        lines = ['=== YouTube Search ===']
        for r in results[:8]:
            title = r.get('title', '?')[:36]
            author = r.get('author', '?')[:16]
            views = r.get('viewCount', 0)
            if views >= 1000000:
                v = views // 1000000
                d = (views % 1000000) // 100000
                v_str = str(v) + '.' + str(d) + 'M'
            elif views >= 1000:
                v = views // 1000
                d = (views % 1000) // 100
                v_str = str(v) + '.' + str(d) + 'K'
            else:
                v_str = str(views)
            lines.append(f'  {title}')
            lines.append(f'    by {author} | {v_str} views')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'ytsearch: {e}')


def cmd_hn(args):
    """Hacker News top stories."""
    try:
        import ujson
        body = _https_get('hacker-news.firebaseio.com', '/v0/topstories.json', timeout=10)
        ids = ujson.loads(body)[:8]
        lines = ['=== Hacker News ===']
        for story_id in ids:
            sb = _https_get('hacker-news.firebaseio.com', f'/v0/item/{story_id}.json', timeout=5)
            story = ujson.loads(sb)
            title = story.get('title', '?')[:44]
            score = story.get('score', 0)
            comments = story.get('descendants', 0)
            lines.append(f'  [{score}|{comments}] {title}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'hn: {e}')


def cmd_so(args):
    """Stack Overflow search."""
    if not args.strip():
        return ('print', 'Usage: so <query>')
    try:
        import ujson
        query = args.strip().replace(' ', '+')
        body = _https_get('api.stackexchange.com', f'/2.3/search?order=desc&sort=votes&intitle={query}&site=stackoverflow&pagesize=8', timeout=10)
        data = ujson.loads(body)
        items = data.get('items', [])
        if not items:
            return ('print', 'so: no results')
        lines = ['=== Stack Overflow ===']
        for item in items[:8]:
            title = item.get('title', '?')[:40]
            score = item.get('score', 0)
            answers = item.get('answer_count', 0)
            lines.append(f'  [{score}|{answers}] {title}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'so: {e}')


def cmd_devto(args):
    """Dev.to top posts."""
    try:
        import ujson
        body = _http_get('dev.to', '/api/articles?per_page=8&top=7', timeout=10)
        data = ujson.loads(body)
        if not data:
            return ('print', 'devto: no posts')
        lines = ['=== Dev.to ===']
        for post in data[:8]:
            title = post.get('title', '?')[:40]
            reactions = post.get('positive_reactions_count', 0)
            comments = post.get('comments_count', 0)
            lines.append(f'  [{reactions}|{comments}] {title}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'devto: {e}')


def cmd_ghtrending(args):
    """GitHub trending repos."""
    try:
        import ujson
        body = _https_get('api.github.com', '/search/repositories?q=stars:>1000&sort=stars&order=desc&per_page=8', timeout=10)
        data = ujson.loads(body)
        items = data.get('items', [])
        if not items:
            return ('print', 'ghtrending: no results')
        lines = ['=== GitHub Trending ===']
        for repo in items[:8]:
            name = repo.get('full_name', '?')[:30]
            stars = repo.get('stargazers_count', 0)
            lang = repo.get('language', '?')[:10]
            if stars >= 1000:
                v = stars // 1000
                d = (stars % 1000) // 100
                s_str = str(v) + '.' + str(d) + 'K'
            else:
                s_str = str(stars)
            lines.append(f'  {name} [{s_str}] {lang}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'ghtrending: {e}')


def _https_post_auth(host, path, payload, token, timeout=30):
    import usocket
    import ssl
    sock = usocket.socket()
    sock.settimeout(timeout)
    addr = usocket.getaddrinfo(host, 443)[0][-1]
    sock.connect(addr)
    ssock = ssl.wrap_socket(sock, server_hostname=host)
    body_bytes = payload.encode('utf-8')
    request = (
        f'POST {path} HTTP/1.1\r\n'
        f'Host: {host}\r\n'
        f'Content-Type: application/json\r\n'
        f'Content-Length: {len(body_bytes)}\r\n'
        f'Authorization: Bearer {token}\r\n'
        f'Connection: close\r\n'
        f'\r\n'
    )
    ssock.sendall(request.encode() + body_bytes)
    data = b''
    while True:
        try:
            chunk = ssock.read(2048)
        except OSError:
            break
        if not chunk:
            break
        data += chunk
    try:
        ssock.close()
    except Exception:
        pass
    raw = data.decode('utf-8', 'ignore')
    header_end = raw.find('\r\n\r\n')
    if header_end < 0:
        header_end = raw.find('\n\n')
    if header_end < 0:
        return raw
    headers = raw[:header_end]
    body = raw[header_end + 4:].lstrip('\r\n')
    if 'Transfer-Encoding: chunked' in headers:
        decoded = b''
        pos = 0
        body_bytes2 = body.encode('utf-8', 'ignore')
        while pos < len(body_bytes2):
            crlf_pos = body_bytes2.find(b'\r\n', pos)
            if crlf_pos < 0:
                break
            try:
                chunk_size = int(body_bytes2[pos:crlf_pos], 16)
            except ValueError:
                break
            if chunk_size == 0:
                break
            decoded += body_bytes2[crlf_pos + 2:crlf_pos + 2 + chunk_size]
            pos = crlf_pos + 2 + chunk_size + 2
        body = decoded.decode('utf-8', 'ignore')
    return body


_BSKY_CFG = '/sd/bsky_config.txt'


def _bsky_load():
    try:
        with open(_BSKY_CFG) as f:
            lines = f.read().strip().split('\n')
            if len(lines) >= 2:
                return lines[0].strip(), lines[1].strip()
    except:
        pass
    return None, None


def _bsky_save(handle, password):
    with open(_BSKY_CFG, 'w') as f:
        f.write(handle + '\n' + password + '\n')


def cmd_bsky(args):
    import ujson
    parts = args.strip().split() if args.strip() else []
    action = parts[0].lower() if parts else ''

    if action == 'login':
        if len(parts) < 3:
            return ('print', 'bsky login [handle] [app-password]\n  e.g. bsky login alice.bsky.social AbCdEfGh')
        handle = parts[1]
        password = parts[2]
        try:
            payload = ujson.dumps({'identifier': handle, 'password': password})
            body = _https_post('bsky.social', '/xrpc/com.atproto.server.createSession', payload, timeout=10)
            j = ujson.loads(body)
            if 'accessJwt' in j:
                _bsky_save(handle, password)
                return ('print', f'bsky: logged in as {handle}')
            else:
                return ('print', 'bsky: login failed')
        except Exception as e:
            return ('print', f'bsky: {e}')

    if action == 'logout':
        try:
            import os
            os.remove(_BSKY_CFG)
        except:
            pass
        return ('print', 'bsky: logged out')

    handle, password = _bsky_load()
    if not handle and action not in ('help', 'login'):
        return ('print', 'bsky: not logged in\n  bsky login [handle] [app-password]')

    if action == '' or action == 'profile':
        target = parts[1] if len(parts) > 1 else handle
        if not target:
            return ('print', 'bsky profile [handle]')
        try:
            body = _https_get('public.api.bsky.app', f'/xrpc/app.bsky.actor.getProfile?actor={target}', timeout=10)
            j = ujson.loads(body)
            name = j.get('displayName', '?')
            handle_str = j.get('handle', '?')
            desc = j.get('description', '')
            followers = j.get('followersCount', 0)
            following = j.get('followsCount', 0)
            posts = j.get('postsCount', 0)
            lines = [f'=== {name} (@{handle_str}) ===']
            if desc:
                for l in _wrap_text(desc, 36):
                    lines.append(f'  {l}')
            lines.append(f'  {posts} posts  {followers} followers  {following} following')
            return ('print_lines', lines)
        except Exception as e:
            return ('print', f'bsky: {e}')

    elif action == 'feed':
        target = parts[1] if len(parts) > 1 else handle
        if not target:
            return ('print', 'bsky feed [handle]')
        try:
            body = _https_get('public.api.bsky.app',
                              f'/xrpc/app.bsky.feed.getAuthorFeed?actor={target}&limit=5', timeout=10)
            j = ujson.loads(body)
            feed = j.get('feed', [])
            if not feed:
                return ('print', f'bsky: no posts from @{target}')
            lines = [f'=== @{target} feed ===']
            for item in feed[:5]:
                post = item.get('post', {})
                record = post.get('record', {})
                text = record.get('text', '')
                likes = post.get('likeCount', 0)
                reposts = post.get('repostCount', 0)
                lines.append('')
                lines.append(f'  [{likes}L {reposts}R]')
                for l in _wrap_text(text, 36):
                    lines.append(f'  {l}')
            return ('print_lines', lines)
        except Exception as e:
            return ('print', f'bsky: {e}')

    elif action == 'search':
        query = ' '.join(parts[1:]) if len(parts) > 1 else ''
        if not query:
            return ('print', 'bsky search [query]')
        try:
            body = _https_get('public.api.bsky.app',
                              f'/xrpc/app.bsky.feed.searchPosts?q={query.replace(" ", "%20")}&limit=5', timeout=10)
            j = ujson.loads(body)
            posts = j.get('posts', [])
            if not posts:
                return ('print', f'bsky: no results for "{query}"')
            lines = [f'=== bsky search: {query} ===']
            for post in posts[:5]:
                author = post.get('author', {}).get('handle', '?')
                text = post.get('record', {}).get('text', '')
                likes = post.get('likeCount', 0)
                lines.append('')
                lines.append(f'  @{author} [{likes}L]')
                for l in _wrap_text(text, 36):
                    lines.append(f'  {l}')
            return ('print_lines', lines)
        except Exception as e:
            return ('print', f'bsky: {e}')

    elif action == 'post':
        text = ' '.join(parts[1:])
        if not text:
            return ('print', 'bsky post [text]')
        try:
            from time import time
            payload = ujson.dumps({
                '$type': 'com.atproto.repo.createRecord',
                'repo': handle,
                'collection': 'app.bsky.feed.post',
                'record': {
                    '$type': 'app.bsky.feed.post',
                    'createdAt': _bsky_timestamp(),
                    'text': text,
                },
            })
            token = password
            session_body = _https_post('bsky.social', '/xrpc/com.atproto.server.createSession',
                                       ujson.dumps({'identifier': handle, 'password': password}), timeout=10)
            session = ujson.loads(session_body)
            jwt = session.get('accessJwt', '')
            if not jwt:
                return ('print', 'bsky: auth failed')
            record_payload = ujson.dumps({
                '$type': 'com.atproto.repo.createRecord',
                'repo': handle,
                'collection': 'app.bsky.feed.post',
                'record': {
                    '$type': 'app.bsky.feed.post',
                    'createdAt': _bsky_timestamp(),
                    'text': text,
                },
            })
            resp = _https_post_auth('bsky.social', '/xrpc/com.atproto.repo.createRecord',
                                    record_payload, jwt, timeout=10)
            r = ujson.loads(resp)
            uri = r.get('uri', '')
            if uri:
                return ('print', f'bsky: posted! {uri}')
            else:
                return ('print', f'bsky: post failed\n  {resp[:80]}')
        except Exception as e:
            return ('print', f'bsky: {e}')

    elif action == 'timeline':
        try:
            session_body = _https_post('bsky.social', '/xrpc/com.atproto.server.createSession',
                                       ujson.dumps({'identifier': handle, 'password': password}), timeout=10)
            session = ujson.loads(session_body)
            jwt = session.get('accessJwt', '')
            if not jwt:
                return ('print', 'bsky: auth failed')
            import usocket
            import ssl
            sock = usocket.socket()
            sock.settimeout(10)
            addr = usocket.getaddrinfo('bsky.social', 443)[0][-1]
            sock.connect(addr)
            ssock = ssl.wrap_socket(sock, server_hostname='bsky.social')
            req = (
                f'GET /xrpc/app.bsky.feed.getTimeline?limit=5 HTTP/1.1\r\n'
                f'Host: bsky.social\r\n'
                f'Authorization: Bearer {jwt}\r\n'
                f'Connection: close\r\n'
                f'\r\n'
            )
            ssock.sendall(req.encode())
            data = b''
            while True:
                try:
                    chunk = ssock.read(2048)
                except OSError:
                    break
                if not chunk:
                    break
                data += chunk
            ssock.close()
            raw = data.decode('utf-8', 'ignore')
            idx = raw.find('\r\n\r\n')
            body = raw[idx + 4:].lstrip('\r\n') if idx >= 0 else raw
            j = ujson.loads(body)
            feed = j.get('feed', [])
            if not feed:
                return ('print', 'bsky: timeline empty')
            lines = ['=== Timeline ===']
            for item in feed[:5]:
                post = item.get('post', {})
                author = post.get('author', {}).get('handle', '?')
                text = post.get('record', {}).get('text', '')
                likes = post.get('likeCount', 0)
                lines.append('')
                lines.append(f'  @{author} [{likes}L]')
                for l in _wrap_text(text, 36):
                    lines.append(f'  {l}')
            return ('print_lines', lines)
        except Exception as e:
            return ('print', f'bsky: {e}')

    elif action == 'help':
        return ('print_lines', [
            '=== Bluesky ===',
            '',
            '  bsky login [handle] [app-password]',
            '  bsky logout',
            '  bsky [handle]      Show profile',
            '  bsky feed [handle]  Recent posts',
            '  bsky timeline      Your feed (auth)',
            '  bsky search [q]    Search posts',
            '  bsky post [text]   Post (auth)',
            '  bsky help',
        ])
    else:
        return ('print', f'bsky: unknown action "{action}"\n  bsky help')


def _bsky_timestamp():
    import time
    t = time.time()
    days = t // 86400
    secs = int(t % 86400)
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    y = 1970
    while days >= 366:
        if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0):
            days -= 366
        else:
            days -= 365
        y += 1
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0):
        month_days[1] = 29
    mo = 0
    while mo < 12 and days >= month_days[mo]:
        days -= month_days[mo]
        mo += 1
    return f'{y}-{mo+1:02d}-{int(days)+1:02d}T{h:02d}:{m:02d}:{s:02d}.000Z'


_GMAIL_CFG = '/sd/gmail_config.txt'


def _imap_connect(email, password):
    import usocket
    import ssl
    sock = usocket.socket()
    sock.settimeout(15)
    addr = usocket.getaddrinfo('imap.gmail.com', 993)[0][-1]
    sock.connect(addr)
    ssock = ssl.wrap_socket(sock, server_hostname='imap.gmail.com')
    banner = ssock.read(1024)
    return ssock


def _imap_cmd(ssock, tag, cmd):
    ssock.sendall(f'{tag} {cmd}\r\n'.encode())
    resp = b''
    while True:
        try:
            chunk = ssock.read(2048)
        except OSError:
            break
        if not chunk:
            break
        resp += chunk
        decoded = resp.decode('utf-8', 'ignore')
        if f'{tag} OK' in decoded or f'{tag} NO' in decoded or f'{tag} BAD' in decoded:
            break
    return resp.decode('utf-8', 'ignore')


def _smtp_connect(email, password):
    import usocket
    import ssl
    import ubinascii
    sock = usocket.socket()
    sock.settimeout(15)
    addr = usocket.getaddrinfo('smtp.gmail.com', 465)[0][-1]
    sock.connect(addr)
    ssock = ssl.wrap_socket(sock, server_hostname='smtp.gmail.com')
    ssock.read(1024)
    ssock.sendall(b'EHLO espelt\r\n')
    ssock.read(1024)
    ssock.sendall(b'AUTH LOGIN\r\n')
    ssock.read(1024)
    ssock.sendall(ubinascii.b2a_base64(email.encode()).strip() + b'\r\n')
    ssock.read(1024)
    ssock.sendall(ubinascii.b2a_base64(password.encode()).strip() + b'\r\n')
    resp = ssock.read(1024)
    if b'235' not in resp:
        ssock.close()
        return None
    return ssock


def _gmail_load():
    try:
        with open(_GMAIL_CFG) as f:
            lines = f.read().strip().split('\n')
            if len(lines) >= 2:
                return lines[0].strip(), lines[1].strip()
    except:
        pass
    return None, None


def _gmail_save(email, password):
    with open(_GMAIL_CFG, 'w') as f:
        f.write(email + '\n' + password + '\n')


def _decode_header(raw):
    result = ''
    i = 0
    while i < len(raw):
        if raw[i:i+2] == '=?':
            end = raw.find('?', i + 2)
            if end < 0:
                result += raw[i:]
                break
            charset_end = raw.find('?', end + 1)
            if charset_end < 0:
                result += raw[i:]
                break
            enc = raw[i+2:end].lower()
            enc_type = raw[end+1:charset_end].upper()
            encoded_end = raw.find('?=', charset_end + 1)
            if encoded_end < 0:
                result += raw[i:]
                break
            data = raw[charset_end+1:encoded_end]
            import ubinascii
            try:
                decoded = ubinascii.a2b_base64(data).decode('utf-8', 'ignore')
                result += decoded
            except:
                result += data
            i = encoded_end + 2
        else:
            result += raw[i]
            i += 1
    return result


def _parse_fetch_body(resp):
    lines = resp.split('\r\n')
    body_lines = []
    in_body = False
    for line in lines:
        if in_body:
            if line.startswith(')') or line.strip().startswith('A') or line.strip().startswith('*'):
                if line.strip().startswith('*') or line.strip().startswith(')'):
                    break
            body_lines.append(line)
        if 'BODY[]' in line or 'BODY[TEXT]' in line:
            in_body = True
            idx = line.find('{')
            if idx >= 0:
                rest = line[idx:]
                brace_end = rest.find('}')
                if brace_end >= 0:
                    body_part = rest[brace_end+1:]
                    if body_part:
                        body_lines.append(body_part)
    return '\n'.join(body_lines)


def cmd_gmail(args):
    """Gmail: read and send emails via IMAP/SMTP."""
    parts = args.strip().split() if args.strip() else []
    action = parts[0].lower() if parts else ''

    if action == 'login':
        if len(parts) < 3:
            return ('print', 'gmail login [email] [app-password]\n  Generate app password at:\n  myaccount.google.com/apppasswords')
        email = parts[1]
        password = parts[2]
        try:
            ssock = _imap_connect(email, password)
            resp = _imap_cmd(ssock, 'A001', f'LOGIN {email} {password}')
            ssock.sendall(b'A002 LOGOUT\r\n')
            ssock.read(512)
            ssock.close()
            if 'A001 OK' in resp:
                _gmail_save(email, password)
                return ('print', f'gmail: logged in as {email}')
            else:
                return ('print', 'gmail: login failed\n  Check email + app password')
        except Exception as e:
            return ('print', f'gmail: {e}')

    if action == 'logout':
        try:
            import os
            os.remove(_GMAIL_CFG)
        except:
            pass
        return ('print', 'gmail: logged out')

    email, password = _gmail_load()
    if not email and action not in ('help', 'login'):
        return ('print', 'gmail: not logged in\n  gmail login [email] [app-password]')

    if action == '' or action == 'inbox':
        try:
            ssock = _imap_connect(email, password)
            _imap_cmd(ssock, 'A001', f'LOGIN {email} {password}')
            _imap_cmd(ssock, 'A002', 'SELECT INBOX')
            resp = _imap_cmd(ssock, 'A003', 'SEARCH ALL')
            _imap_cmd(ssock, 'A099', 'LOGOUT')
            ssock.close()

            ids_str = ''
            idx = resp.find('* SEARCH')
            if idx >= 0:
                end = resp.find('\r\n', idx)
                ids_str = resp[idx+9:end].strip()
            if not ids_str:
                return ('print', 'gmail: inbox empty')

            all_ids = ids_str.split()
            recent = all_ids[-10:]
            recent.reverse()

            ssock = _imap_connect(email, password)
            _imap_cmd(ssock, 'A001', f'LOGIN {email} {password}')
            _imap_cmd(ssock, 'A002', 'SELECT INBOX')

            lines = ['=== Inbox ===']
            for mid in recent:
                resp = _imap_cmd(ssock, f'F{mid}', f'FETCH {mid} (BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
                from_hdr = ''
                subj_hdr = ''
                for line in resp.split('\r\n'):
                    ll = line.lower()
                    if ll.startswith('from:'):
                        from_hdr = _decode_header(line[5:].strip())
                    elif ll.startswith('subject:'):
                        subj_hdr = _decode_header(line[8:].strip())
                lines.append('')
                lines.append(f'  #{mid} {subj_hdr[:36]}')
                lines.append(f'    from: {from_hdr[:36]}')

            _imap_cmd(ssock, 'A099', 'LOGOUT')
            ssock.close()
            return ('print_lines', lines)
        except Exception as e:
            return ('print', f'gmail: {e}')

    elif action == 'read':
        if len(parts) < 2:
            return ('print', 'gmail read [id]')
        mid = parts[1]
        try:
            ssock = _imap_connect(email, password)
            _imap_cmd(ssock, 'A001', f'LOGIN {email} {password}')
            _imap_cmd(ssock, 'A002', 'SELECT INBOX')
            resp = _imap_cmd(ssock, 'A003', f'FETCH {mid} (BODY[HEADER.FIELDS (FROM TO SUBJECT DATE)])')
            _imap_cmd(ssock, 'A004', f'FETCH {mid} BODY[TEXT]')
            body_resp = resp
            header_lines = []
            for line in resp.split('\r\n'):
                ll = line.lower()
                if ll.startswith('from:') or ll.startswith('to:') or ll.startswith('subject:') or ll.startswith('date:'):
                    header_lines.append(line.strip())

            # Get body
            ssock.sendall(f'A005 FETCH {mid} BODY[TEXT]\r\n'.encode())
            body_data = b''
            found_open = False
            while True:
                try:
                    chunk = ssock.read(4096)
                except OSError:
                    break
                if not chunk:
                    break
                body_data += chunk
                bd = body_data.decode('utf-8', 'ignore')
                if f'A005 OK' in bd:
                    break

            _imap_cmd(ssock, 'A099', 'LOGOUT')
            ssock.close()

            body_str = body_data.decode('utf-8', 'ignore')
            # Extract body text
            body_text = ''
            idx = body_str.find('\r\n\r\n')
            if idx >= 0:
                raw_body = body_str[idx+4:]
                # Find end of fetch
                end = raw_body.rfind('\r\nA005')
                if end < 0:
                    end = raw_body.rfind('\r\n)')
                if end > 0:
                    raw_body = raw_body[:end]
                body_text = raw_body.strip()

            lines = [f'=== Email #{mid} ===']
            for hl in header_lines:
                lines.append(f'  {hl[:50]}')
            if body_text:
                lines.append('')
                for bl in body_text.split('\n')[:12]:
                    lines.append(f'  {bl.strip()[:48]}')
            return ('print_lines', lines)
        except Exception as e:
            return ('print', f'gmail: {e}')

    elif action == 'send':
        if len(parts) < 4:
            return ('print', 'gmail send [to] [subject] [body]\n  Underscores become spaces in body')
        to_addr = parts[1]
        subject = parts[2].replace('_', ' ')
        body = ' '.join(parts[3:]).replace('_', ' ')
        try:
            ssock = _smtp_connect(email, password)
            if not ssock:
                return ('print', 'gmail: SMTP auth failed')
            ssock.sendall(f'MAIL FROM:<{email}>\r\n'.encode())
            ssock.read(1024)
            ssock.sendall(f'RCPT TO:<{to_addr}>\r\n'.encode())
            ssock.read(1024)
            ssock.sendall(b'DATA\r\n')
            ssock.read(1024)
            msg = f'From: {email}\r\nTo: {to_addr}\r\nSubject: {subject}\r\n\r\n{body}\r\n.\r\n'
            ssock.sendall(msg.encode())
            resp = ssock.read(1024)
            ssock.sendall(b'QUIT\r\n')
            ssock.read(512)
            ssock.close()
            if b'250' in resp or b'2.0.0' in resp:
                return ('print', f'gmail: sent to {to_addr}')
            else:
                return ('print', f'gmail: send failed')
        except Exception as e:
            return ('print', f'gmail: {e}')

    elif action == 'search':
        query = ' '.join(parts[1:]) if len(parts) > 1 else 'ALL'
        if not query:
            query = 'ALL'
        try:
            ssock = _imap_connect(email, password)
            _imap_cmd(ssock, 'A001', f'LOGIN {email} {password}')
            _imap_cmd(ssock, 'A002', 'SELECT INBOX')
            resp = _imap_cmd(ssock, 'A003', f'SEARCH {query}')
            _imap_cmd(ssock, 'A099', 'LOGOUT')
            ssock.close()

            idx = resp.find('* SEARCH')
            if idx < 0:
                return ('print', 'gmail: no results')
            end = resp.find('\r\n', idx)
            ids_str = resp[idx+9:end].strip()
            if not ids_str:
                return ('print', 'gmail: no results')
            all_ids = ids_str.split()
            recent = all_ids[-10:]
            recent.reverse()

            ssock = _imap_connect(email, password)
            _imap_cmd(ssock, 'A001', f'LOGIN {email} {password}')
            _imap_cmd(ssock, 'A002', 'SELECT INBOX')

            lines = [f'=== Search: {query} ({len(all_ids)} results) ===']
            for mid in recent:
                resp = _imap_cmd(ssock, f'F{mid}', f'FETCH {mid} (BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
                from_hdr = ''
                subj_hdr = ''
                for line in resp.split('\r\n'):
                    ll = line.lower()
                    if ll.startswith('from:'):
                        from_hdr = _decode_header(line[5:].strip())
                    elif ll.startswith('subject:'):
                        subj_hdr = _decode_header(line[8:].strip())
                lines.append('')
                lines.append(f'  #{mid} {subj_hdr[:36]}')
                lines.append(f'    from: {from_hdr[:36]}')

            _imap_cmd(ssock, 'A099', 'LOGOUT')
            ssock.close()
            return ('print_lines', lines)
        except Exception as e:
            return ('print', f'gmail: {e}')

    elif action == 'help':
        return ('print_lines', [
            '=== Gmail ===',
            '',
            '  gmail login [email] [app-pw]',
            '  gmail logout',
            '  gmail inbox        List recent',
            '  gmail read [id]    Read email',
            '  gmail send [to] [subject] [body]',
            '  gmail search [query]',
            '  gmail help',
            '',
            '  Generate app password at:',
            '  myaccount.google.com/apppasswords',
        ])
    else:
        return ('print', f'gmail: unknown "{action}"\n  gmail help')
