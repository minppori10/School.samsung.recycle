import csv
from urllib.request import urlopen
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 구글 스프레드시트 실시간 CSV 주소 연동
SHEET_ID = "1-bSsM-fyNLy9P7d0QA1Wi6kXc2IYYrZh1DucjDXg6-g"
SHEET_URL = f"https://google.com{SHEET_ID}/export?format=csv"

# 🟢 [디자인 추가] 모든 페이지에 공통으로 들어갈 세련된 네비게이션 바와 CSS 디자인 틀입니다.
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>삼성여고 슬기로운 분리수거 생활</title>
    <style>
        body { 
            font-family: 'Malgun Gothic', -apple-system, sans-serif; 
            max-width: 600px; 
            margin: 0 auto; 
            padding: 20px; 
            line-height: 1.6; 
            background-color: #fafbfc;
            color: #2c3e50;
        }
        nav { 
            text-align: center; 
            margin-bottom: 30px; 
            background: white; 
            padding: 12px; 
            border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        nav a { 
            margin: 0 10px; 
            text-decoration: none; 
            color: #7f8c8d; 
            font-weight: bold;
            font-size: 15px;
            transition: color 0.2s;
        }
        nav a:hover { color: #2ecc71; }
        
        /* 컨텐츠 카드 디자인 */
        .card {
            background: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            margin-bottom: 20px;
        }
        h1, h2 { color: #2ecc71; text-align: center; margin-top: 0; }
        p { color: #34495e; word-break: keep-all; }
        
        /* 검색창 및 버튼 스타일 */
        .search-box { display: flex; gap: 10px; margin: 20px 0; }
        input[type="text"] { 
            flex: 1; 
            padding: 12px 16px; 
            font-size: 16px; 
            border: 2px solid #e2e8f0; 
            border-radius: 8px; 
            outline: none;
            transition: border-color 0.2s;
        }
        input[type="text"]:focus { border-color: #2ecc71; }
        button { 
            padding: 12px 24px; 
            font-size: 16px; 
            background-color: #2ecc71; 
            color: white; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: bold;
            transition: background 0.2s;
        }
        button:hover { background-color: #27ae60; }
        
        /* 결과 카드 디자인 */
        .result-card { 
            background: #f9fbf9; 
            border-left: 5px solid #2ecc71; 
            padding: 18px; 
            margin-top: 15px; 
            border-radius: 0 8px 8px 0; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }
        .result-title { font-size: 18px; font-weight: bold; color: #2c3e50; margin: 0 0 8px 0; }
        .result-method { margin: 0; color: #57606f; font-size: 15px; }
        .no-result { color: #e74c3c; text-align: center; font-weight: bold; margin-top: 25px; }
        .badge { display: inline-block; background: #e8f8f5; color: #117a65; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; vertical-align: middle; margin-left: 5px; }
    </style>
</head>
<body>
    <nav>
        <a href="/">홈</a> 
        <a href="/recycle">분리수거 검색</a> 
        <a href="/introduce">프로젝트 소개</a>
    </nav>
    <div class="card">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    content = """
    <h1>삼성여고 슬기로운 분리수거 생활♻️</h1>
    <p style="text-align: center; font-size: 17px; color: #7f8c8d; margin-bottom: 25px;">올바른 재활용 배출 지침 검색 시스템</p>
    <p style="text-align: center; font-size: 15px; background: #f8f9fa; padding: 15px; border-radius: 8px;">
        상단의 <b>[분리수거 검색]</b> 메뉴를 터치하여<br> 버리려는 쓰레기의 품목을 입력해보세요.
    </p>
    """
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", content))

@app.route('/recycle', methods=['GET'])
def recycle():
    keyword = request.args.get('keyword', '').strip()
    results = []

    if keyword:
        try:
            response = urlopen(SHEET_URL)
            lines = [line.decode('utf-8').strip() for line in response.readlines() if line.strip()]
            
            reader = csv.reader(lines)
            all_rows = list(reader)
            
            if all_rows:
                header = [h.strip() for h in all_rows[0]]
                col_품목 = header[0]
                col_방법 = header[1] if len(header) > 1 else header[0]
                
                for row_data in all_rows[1:]:
                    if len(row_data) >= len(header):
                        row_dict = dict(zip(header, [r.strip() for r in row_data]))
                        품목_value = row_dict.get(col_품목, '')
                        방법_value = row_dict.get(col_방법, '')
                        
                        if keyword.lower() in 품목_value.lower():
                            results.append({
                                '품목': 품목_value,
                                '방법': 방법_value
                            })
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")

    # 검색 폼 생성 (value="" 리셋 반영)
    content = f"""
    <h2>🔍 우리 학교 분리수거 검색</h2>
    <form action="/recycle" method="GET" class="search-box">
        <input type="text" name="keyword" placeholder="예: 우유팩, 페트병, 지우개" value="">
        <button type="submit">검색</button>
    </form>
    """

    if keyword:
        if results:
            content += f"<p style='color:#7f8c8d; font-size:14px;'>'<b>{keyword}</b>' 검색 결과 (총 {len(results)}건):</p>"
            for item in results:
                content += f"""
                <div class="result-card">
                    <p class="result-method"><b>방법:</b> {item['방법']}</p>
                </div>
                """
        else:
            content += f"<p class='no-result'>❌ '{keyword}'에 대한 배출 방법이 등록되지 않았습니다.<br><span style='font-size:13px; font-weight:normal; color:#7f8c8d;'>일반쓰레기 배출을 고려하시거나 소개 페이지의 이메일로 문의주세요.</span></p>"

    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", content))

@app.route('/introduce')
def introduce():
    content = """
    <h2>📋 프로젝트 소개</h2>
    <p style="line-height: 1.8;">
        이 웹앱은 학교 내 자원 순환을 장려하기 위해 기획된 <b>'도파민 프로젝트'</b>입니다.
    </p>
    <p style="line-height: 1.8; background: #fffde7; padding: 12px; border-radius: 8px; border-left: 4px solid #f1c40f; font-size: 14px;">
        📌 구글 스프레드시트와 24시간 실시간 연동되어 새로운 품목이 추가되면 즉시 검색 데이터에 반영됩니다.
    </p>
    <div style="margin-top: 25px; padding-top: 15px; border-top: 1px solid #eee;">
        <p style="margin: 5px 0;"><b>📧 문의 사항:</b> bonajohn3409@gmail.com</p>
    </div>
    """
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", content))

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
