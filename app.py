import pandas as pd
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 구글 스프레드시트 실시간 CSV 주소 연동 (기존 ID 그대로 유지)
SHEET_ID = "1-bSsM-fyNLy9P7d0QA1Wi6kXc2IYYrZh1DucjDXg6-g"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

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
            df = pd.read_csv(SHEET_URL)
            search_df = df[df['품목'].astype(str).str.contains(keyword, na=False, case=False)]
            results = search_df.to_dict(orient='records')
        except Exception as e:
            print(f"❌ 구글 시트 데이터 로드 실패: {e}")

    # 💡 [리셋 기능 반영] value="" 로 비워두어 검색 후 입력창이 자동으로 지워집니다.
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
                <p><b>• 품목:</b> {item.get('품목', '정보 없음')}</p>
                <p><b>• 방법:</b> {item.get('방법', '정보 없음')}</p>
                <hr>
                """
        else:
            content += f"<p style='color:red;'>❌ '{keyword}'에 대한 배출 방법이 등록되지 않았거나 일반쓰레기입니다. 자세한 사항은 소개 페이지의 이메일로 문의해주세요.</p>"

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
    # 렌더 클라우드 호스팅 전용 대문 개방 설정
    app.run(host='0.0.0.0', port=5000)
