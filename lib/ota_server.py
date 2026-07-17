import usocket
import ujson
import gc
import os
import time


def _check_network():
    try:
        import network
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            return False
        ip = wlan.ifconfig()[0]
        return ip.startswith('192.168.4.') or ip.startswith('10.0.0.') or ip.startswith('192.168.1.')
    except:
        return False


def _send_html(s, code, body):
    s.sendall(f'HTTP/1.1 {code}\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{body}'.encode())


def _send_json(s, data):
    body = ujson.dumps(data)
    s.sendall(f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{body}'.encode())


def _handle_upload(data):
    header_end = data.find(b'\r\n\r\n')
    if header_end < 0:
        return {'error': 'Invalid request'}
    header = data[:header_end].decode()
    body = data[header_end + 4:]

    filename = None
    for part in header.split('\r\n'):
        if 'filename=' in part:
            start = part.find('filename="') + 10
            end = part.find('"', start)
            if start > 9 and end > start:
                filename = part[start:end]

    if not filename:
        return {'error': 'No filename'}

    if not filename.endswith('.py'):
        return {'error': 'Only .py files allowed'}

    if '/' in filename or '..' in filename:
        return {'error': 'Invalid filename'}

    try:
        with open(filename, 'w') as f:
            f.write(body.decode())
        return {'ok': True, 'file': filename, 'size': len(body)}
    except Exception as e:
        return {'error': str(e)}


def start_ota_server(port=80):
    if not _check_network():
        return False, 'Not on trusted network'

    server = usocket.socket()
    server.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(1)
    server.settimeout(None)

    HTML = '''<!DOCTYPE html>
<html><head><title>Espelt OTA</title>
<style>
body{font-family:monospace;background:#111;color:#0f0;text-align:center;padding:40px}
h1{color:#0ff}input[type=file]{color:#0f0}input[type=submit]{background:#0f0;color:#111;border:none;padding:10px 30px;font-size:16px;cursor:pointer;margin:10px}
input[type=submit]:hover{background:#0ff}pre{background:#222;padding:15px;text-align:left;display:inline-block}
.card{background:#222;padding:20px;margin:20px auto;max-width:400px;border:1px solid #0f0}
</style></head><body>
<h1>Espelt OTA</h1>
<div class="card">
<p>Upload a .py file to update</p>
<form method="POST" enctype="multipart/form-data" action="/upload">
<input type="file" name="file" accept=".py"><br>
<input type="submit" value="Upload & Reboot">
</form></div>
<div class="card">
<h2>Web REPL</h2>
<p>Connect via browser:</p>
<pre>ws://''' + _get_ip() + ''':8266</pre>
<p>Password: espelt2024</p>
</div>
<div class="card">
<p><small>Espelt OS v1.0 | OTA Server</small></p>
</div>
</body></html>'''

    print(f'ota: server running on port {port}')
    print(f'ota: open http://{_get_ip()} in browser')

    while True:
        try:
            client, addr = server.accept()
            client.settimeout(5)
            request = client.recv(2048)

            if not request:
                client.close()
                continue

            first_line = request.split(b'\r\n')[0].decode()
            method = first_line.split(' ')[0] if ' ' in first_line else ''

            if method == 'GET':
                _send_html(client, '200 OK', HTML)
            elif method == 'POST' and b'/upload' in request:
                result = _handle_upload(request)
                if result.get('ok'):
                    _send_html(client, '200 OK',
                        f'<html><body style="background:#111;color:#0f0;font-family:monospace;text-align:center;padding:40px">'
                        f'<h1>Upload OK!</h1><p>{result["file"]} ({result["size"]} bytes)</p>'
                        f'<p>Rebooting in 3 seconds...</p>'
                        f'<script>setTimeout(()=>window.close(),3000)</script>'
                        f'</body></html>')
                    client.close()
                    time.sleep(3)
                    import machine
                    machine.reset()
                    return
                else:
                    _send_html(client, '400 Bad Request',
                        f'<html><body style="background:#111;color:#f00;font-family:monospace;text-align:center;padding:40px">'
                        f'<h1>Error: {result["error"]}</h1><p><a href="/" style="color:#0ff">Back</a></p>'
                        f'</body></html>')
            else:
                _send_html(client, '404 Not Found', '<html><body style="background:#111;color:#f00;font-family:monospace;text-align:center;padding:40px"><h1>404</h1></body></html>')
            client.close()
        except Exception as e:
            print(f'ota: {e}')
            try:
                client.close()
            except:
                pass


def _get_ip():
    try:
        import network
        wlan = network.WLAN(network.STA_IF)
        return wlan.ifconfig()[0] if wlan.isconnected() else '0.0.0.0'
    except:
        return '0.0.0.0'
