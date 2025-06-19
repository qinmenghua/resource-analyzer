from flask import Flask, request, jsonify
import re
import requests

app = Flask(__name__)

def analyze_link(link):
    if link.startswith('magnet:?'):
        # 支持 base16 (40位 hex) 和 base32 (32位字母数字)
        match = re.search(r'btih:([a-zA-Z0-9]{32,40})', link)
        info_hash = match.group(1) if match else None

        # 提取文件名（dn 参数）
        filename_match = re.search(r'dn=([^&]+)', link)
        filename = filename_match.group(1) if filename_match else '未知'

        return {
            'type': '磁力链接',
            'filename': filename,
            'size': '未知',
            'screenshot': f'https://image.thum.io/get/width/640/crop/768/https://itorrents.org/torrent/{info_hash}.torrent' if info_hash else None
        }

    elif link.startswith('ed2k://'):
        parts = link.strip().split('|')
        if len(parts) >= 4:
            try:
                size_mb = int(parts[3]) // (1024 * 1024)
            except:
                size_mb = '未知'
            return {
                'type': 'ED2K链接',
                'filename': parts[2],
                'size': f"{size_mb} MB" if isinstance(size_mb, int) else '未知',
                'screenshot': None
            }

    elif link.startswith('http'):
        try:
            head = requests.head(link, allow_redirects=True, timeout=5)
            size = int(head.headers.get('Content-Length', 0))
            filename = link.split('/')[-1]
            return {
                'type': '直链 (DDL)',
                'filename': filename or '未知',
                'size': f"{size // (1024 * 1024)} MB" if size else '未知',
                'screenshot': f"https://image.thum.io/get/width/640/{link}"
            }
        except Exception:
            return {
                'type': '直链 (DDL)',
                'filename': '未知',
                'size': '未知',
                'screenshot': None
            }

    return {'error': '无法识别的链接类型'}

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    link = data.get('link')
    if not link:
        return jsonify({'error': '请提供链接'}), 400
    result = analyze_link(link)
    return jsonify(result)
