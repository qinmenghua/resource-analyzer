from flask import Flask, request, jsonify
import re, requests

app = Flask(__name__)

def analyze_link(link):
    if link.startswith('magnet:?'):
        match = re.search(r'btih:([a-fA-F0-9]+)', link)
        info_hash = match.group(1) if match else '未知'
        return {
            'type': '磁力链接',
            'filename': re.search(r'dn=([^&]+)', link).group(1) if 'dn=' in link else '未知',
            'size': '未知',
            'screenshot': f'https://image.thum.io/get/width/640/crop/768/https://itorrents.org/torrent/{info_hash}.torrent'
        }
    elif link.startswith('ed2k://'):
        parts = link.strip().split('|')
        if len(parts) >= 4:
            return {
                'type': 'ED2K链接',
                'filename': parts[2],
                'size': f"{int(parts[3]) // (1024 * 1024)} MB",
                'screenshot': None
            }
    elif link.startswith('http'):
        try:
            head = requests.head(link, allow_redirects=True, timeout=5)
            size = int(head.headers.get('Content-Length', 0))
            filename = link.split('/')[-1]
            return {
                'type': '直链 (DDL)',
                'filename': filename,
                'size': f"{size // (1024 * 1024)} MB" if size else '未知',
                'screenshot': f"https://image.thum.io/get/width/640/{link}"
            }
        except Exception:
            return { 'type': 'DDL', 'filename': '未知', 'size': '未知', 'screenshot': None }
    return {'error': '无法识别的链接类型'}

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    link = data.get('link')
    if not link:
        return jsonify({'error': '请提供链接'}), 400
    result = analyze_link(link)
    return jsonify(result)
