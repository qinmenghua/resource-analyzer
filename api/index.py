from flask import Flask, request, jsonify
import re
import requests

app = Flask(__name__)

def analyze_link(link):
    # 简化的示例代码，或者用你的完整逻辑
    if link.startswith('magnet:?'):
        match = re.search(r'btih:([a-zA-Z0-9]{32,40})', link)
        info_hash = match.group(1) if match else None
        filename_match = re.search(r'dn=([^&]+)', link)
        filename = filename_match.group(1) if filename_match else '未知'
        return {
            'type': '磁力链接',
            'filename': filename,
            'size': '未知',
            'screenshot': f'https://image.thum.io/get/width/640/crop/768/https://itorrents.org/torrent/{info_hash}.torrent' if info_hash else None
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

# **关键**，必须是这样导出：
handler = app
