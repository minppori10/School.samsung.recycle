import csv
from urllib.request import urlopen
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 구글 스프레드시트 실시간 CSV 주소 연동 (기존 ID 그대로 유지)
SHEET_ID = "1-bSsM-fyNLy9P7d0QA1Wi6kXc2IYYrZh1DucjDXg6-g"
SHEET_URL = f"https://google.com{SHEET_ID}/export?format=csv"

# 내비게이션 메뉴바 HTML
MENU_HTML = """
<div style="background-color: #eee; padding: 10px;">
    <a href="/">홈</a> |
    <a href="/recycle">분리수거 검색</a> |
    <a href="/introduce">프로젝트 소개</a>
</div>
<br>
"""

@app.route('/')
def home():
    content = """
    <h1>도파민 프로젝트</h1>
    <p>분리수거 항목을 검색해보세요.</p>
    <p>상단의 [분리수거 검색] 메뉴를 클릭하면 이동합니다.</p>
    """
    return MENU_HTML + content

@app.route('/recycle', methods=['GET'])
def recycle():
    keyword = request.args.get('keyword', '').strip()
    results = []

    if keyword:
        try:
            # 🟢 [초경량 파싱] Pandas 없이 구글 시트 URL에서 CSV 데이터를 바로 한 줄씩 읽어옵니다.
            response = urlopen(SHEET_URL)
            lines = [line.decode('utf-8') for line in response.readlines()]
            reader = csv.DictReader(lines)
            
            for row in reader:
                # 구글 시트의 '품목' 열에 검색어가 포함되어 있는지 검사 (대소문자 무시)
                if keyword.lower() in str(row.get('품목', '')).lower():
                    results.append({
                        '품목': row.get('품목', '정보 없음'),
                        '배출방법': row.get('배출방법', row.get('방법', '정보 없음'))
                    })
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")

    # 검색 창 (value=""로 리셋 반영)
    content = f"""
    <h2>우리 학교 분리수거 검색기</h2>
    <form action="/recycle" method="GET">
        <input type="text" name="keyword" placeholder="검색할 품목 입력" value="">
        <button type="submit">검색</button>
    </form>
    <hr>
    """

    if keyword:
        if results:
            content += f"<p>'{keyword}' 검색 결과 총 {len(results)}건입니다.</p>"
            for item in results:
                content += f"""
                <p><b>• 품목:</b> {item['품목']}</p>
                <p><b>• 방법:</b> {item['배출방법']}</p>
                <hr>
                """
        else:
            content += f"<p style='color:red;'>❌ '{keyword}'에 대한 배출 방법이 등록되지 않았습니다.</p>"

    return MENU_HTML + content

@app.route('/introduce')
def introduce():
    content = """
    <h2>프로젝트 소개 페이지</h2>
    <p>이 웹앱은 학교 내 올바른 분리배출을 장려하는 '도파민 프로젝트'의 일환입니다.</p>
    <p>구글 스프레드시트와 실시간 연동되어 상시 수정이 가능합니다.</p>
    <p>분리수거와 관련된 문의 사항은 아래 이메일로 문의 바랍니다.</p>
    <p><b>문의 이메일: bonajohn3409@gmail.com </b></p>
    """
    return MENU_HTML + content

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
