# ===========================================================
# Semi-project : To Do App
# ===========================================================

# -------------------------
# 라이브러리 호출
# -------------------------
import datetime as dt
import json, csv, os
import streamlit as st
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie

# -------------------------
# 파일 경로
# -------------------------
DATA_JSON = "data.json"
DATA_CSV  = "data.csv"

# ==========[ 함수 ]=========================================

# --------------------------------
# 데이터 로딩 / 저장 (안정성 강화)
# --------------------------------
def load_items():
    """
    JSON / CSV 파일을 안전하게 로드
    - 파일이 없거나
    - JSON이 깨졌거나
    - CSV 헤더만 있는 경우
    → 빈 리스트 반환
    """
    try:
        if st.session_state["storage"] == "CSV" and os.path.exists(DATA_CSV):
            with open(DATA_CSV, newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        else:
            with open(DATA_JSON, "r", encoding="utf-8-sig") as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_items(items):
    """선택된 저장 방식(JSON / CSV)에 따라 저장"""
    if st.session_state["storage"] == "CSV":
        with open(DATA_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["description", "date", "time", "status"]
            )
            writer.writeheader()
            writer.writerows(items)
    else:
        with open(DATA_JSON, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

# --------------------------------
# 유틸 함수
# --------------------------------
def is_today(date_str: str) -> bool:
    """마감일이 오늘인지 확인"""
    return date_str == dt.date.today().isoformat()

@st.cache_data
def load_lottie():
    """Lottie JSON 캐싱 로드"""
    with open("lottie-load.json", "r", encoding="utf-8-sig") as f:
        return json.load(f)

# --------------------------------
# HTML + CSS 
# --------------------------------
def makeHTML(body: str) -> str:
    return f"""
    <style>
    .container {{
        border: 3px double black;
        border-radius: 8px;
        padding: 5px;
    }}

    .item_pending {{
        background: rgba(0,200,0,0.25);
        border-left: 6px solid green;
        padding: 6px;
    }}

    .item_priority {{
        background: rgba(255,165,0,0.30);
        border-left: 6px solid orange;
        padding: 6px;
        font-weight: bold;
    }}

    .item_done {{
        background: rgba(180,180,180,0.40);
        border-left: 6px solid gray;
        padding: 6px;
        text-decoration: line-through;
        color: #555;
    }}

    .active {{
        border: 3px solid crimson;
        background: rgba(255,0,0,0.08);
        margin: 6px;
    }}

    .inactive {{
        margin: 6px;
    }}

    .today {{
        box-shadow: 0 0 10px gold;
    }}

    .title {{
        font-size: 42px;
        font-weight: 800;
        color: darkred;
    }}

    p.desc {{
        font-size: 20px;
        margin: 4px 10px;
    }}

    p.time {{
        font-size: 14px;
        margin: 2px 10px;
    }}
    </style>

    <div class="container">
        {body}
    </div>
    """

# --------------------------------
# UI 렌더링 함수
# --------------------------------
def render_header():
    """상단 로고 + 타이틀"""
    col1, col2 = st.columns([1, 2])

    with col1:
        st_lottie(load_lottie(), height=140)

    with col2:
        components.html(
            '<div class="title" ' \
            'style="' \
              'display:inline-block;' \
              'font-size:40px;' \
              'padding:10px 15px;' \
              'margin-top:30px;' \
              'border:2px solid red;' \
              'background:#fff;">To Do List</div>',
            height=120
        )

def render_buttons(items):
    """오른쪽 버튼 영역"""
    if st.button("🔺") and st.session_state["pos"] > 0:
        st.session_state["pos"] -= 1
        st.rerun()

    if st.button("🔻") and st.session_state["pos"] < len(items) - 1:
        st.session_state["pos"] += 1
        st.rerun()

    # DONE / UNDO 토글
    if len(items) > 0:
        label = "UNDO" if items[st.session_state["pos"]]["status"] == "Done" else "DONE"
        if st.button(label):
            items[st.session_state["pos"]]["status"] = (
                "Pending" if items[st.session_state["pos"]]["status"] == "Done" else "Done"
            )
            save_items(items)
            st.rerun()

    if st.button("ADD"):
        st.session_state["mode"] = "add"

    if st.button("EDIT") and len(items) > 0:
        st.session_state["mode"] = "edit"

def render_list(items):
    """필터가 적용된 할 일 목록 렌더링"""
    body = ""

    for i, item in enumerate(items):
        current = "active" if i == st.session_state["pos"] else "inactive"
        status_class = "item_" + item["status"].lower()

        icon = ""
        if item["status"] == "Priority":
            icon = "🔥 "
        elif item["status"] == "Done":
            icon = "✔️ "

        today_class = "today" if is_today(item["date"]) else ""

        body += f"""
        <div class="{current} {today_class}">
            <div class="{status_class}">
                <p class="desc">{icon}{item['description']}</p>
                <p class="time">{item['date']} {item['time']}</p>
            </div>
        </div>
        """

    components.html(makeHTML(body), height=700, scrolling=True)

def render_add_form(items):
    """할 일 추가 폼"""
    with st.form("add"):
        what = st.text_input("TO DO")
        date = str(st.date_input("DATE"))
        time = str(st.time_input("TIME"))
        status = st.selectbox("STATUS", ["Pending", "Priority"])

        if st.form_submit_button("CONFIRM"):
            items.append({
                "description": what,
                "date": date,
                "time": time,
                "status": status
            })
            save_items(items)
            st.session_state["pos"] = len(items) - 1
            st.session_state["mode"] = "list"
            st.rerun()

def render_edit_form(items):
    """할 일 수정 폼"""
    item = items[st.session_state["pos"]]

    with st.form("edit"):
        what = st.text_input("TO DO", item["description"])
        date = str(st.date_input("DATE", dt.datetime.strptime(item["date"], "%Y-%m-%d")))
        time = str(st.time_input("TIME", dt.datetime.strptime(item["time"], "%H:%M:%S")))
        status = st.selectbox(
            "STATUS",
            ["Pending", "Priority", "Done"],
            index=["Pending", "Priority", "Done"].index(item["status"])
        )

        if st.form_submit_button("CONFIRM"):
            items[st.session_state["pos"]] = {
                "description": what,
                "date": date,
                "time": time,
                "status": status
            }
            save_items(items)
            st.session_state["mode"] = "list"
            st.rerun()

# ==========[ Main ]=========================================

# --------------------------------
# 세션 초기화
# --------------------------------
st.session_state.setdefault("pos", 0)
st.session_state.setdefault("mode", "list")
st.session_state.setdefault("storage", "JSON")

# --------------------------------
# 사이드바 UI
# --------------------------------
st.sidebar.selectbox("저장 방식", ["JSON", "CSV"], key="storage")
filter_selected = st.sidebar.selectbox(
    "상태 필터",
    ["전체", "Pending", "Priority", "Done"]
)

# --------------------------------
# 데이터 로드
# --------------------------------
items = load_items()

# --------------------------------
# 완료 통계 그래프 (원본 기준)
# --------------------------------
status_count = {
    "Pending": 0,
    "Priority": 0,
    "Done": 0
}
for item in items:
    status_count[item["status"]] += 1

st.sidebar.bar_chart(status_count)

# --------------------------------
# 필터 적용
# --------------------------------
if filter_selected == "전체":
    filtered_items = items
else:
    filtered_items = [item for item in items if item["status"] == filter_selected]

# --------------------------------
# 헤더
# --------------------------------
render_header()

# --------------------------------
# 메인 레이아웃
# --------------------------------
left, right = st.columns([6, 1])

with right:
    render_buttons(items)

with left:
    if st.session_state["mode"] == "add":
        render_add_form(items)
    elif st.session_state["mode"] == "edit":
        render_edit_form(items)

    render_list(filtered_items)

