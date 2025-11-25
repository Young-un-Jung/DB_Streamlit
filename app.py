import streamlit as st
import pandas as pd
import duckdb
import os
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 설정
# ---------------------------------------------------------
st.set_page_config(page_title="마당서점 관리", layout="wide", initial_sidebar_state="collapsed")
st.title("📚 마당서점 (SQL 파일 연동)")

# ---------------------------------------------------------
# 2. 데이터베이스 연결 및 초기화 (핵심!)
# ---------------------------------------------------------
# SQL 파일명 (사진에 있는 이름 그대로!)
SQL_FILE_NAME = "demo_madang_init.sql"

def get_db_connection():
    """
    세션 상태(session_state)에 DB 연결을 저장해서, 
    버튼을 누를 때마다 DB가 초기화되는 것을 방지합니다.
    """
    if 'con' not in st.session_state:
        # 1. 메모리 DB 생성
        con = duckdb.connect(database=':memory:')
        
        # 2. SQL 파일 읽어서 실행
        if os.path.exists(SQL_FILE_NAME):
            try:
                with open(SQL_FILE_NAME, "r", encoding="utf-8") as f:
                    init_script = f.read()
                con.execute(init_script)
                # st.toast(f"✅ {SQL_FILE_NAME} 로드 성공!") # (디버깅용 알림)
            except Exception as e:
                st.error(f"❌ SQL 파일 실행 중 오류: {e}")
                st.stop()
        else:
            st.error(f"🚨 '{SQL_FILE_NAME}' 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
            st.stop()
        
        # 3. 세션에 저장
        st.session_state.con = con
    
    return st.session_state.con

# DB 연결 가져오기
con = get_db_connection()

# ---------------------------------------------------------
# 3. 세션 변수 초기화 (고객 선택 상태 유지)
# ---------------------------------------------------------
if 'selected_custid' not in st.session_state:
    st.session_state.selected_custid = None
if 'selected_name' not in st.session_state:
    st.session_state.selected_name = ""

# ---------------------------------------------------------
# 4. 탭 구성 (UI)
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🔍 고객 조회 & 등록", "🛒 도서 주문", "📊 서점 현황"])

# --- [Tab 1] 고객 관리 ---
with tab1:
    st.header("고객 찾기")
    col1, col2 = st.columns([3, 1])
    with col1:
        search_name = st.text_input("고객 이름 입력", placeholder="예: 박지성", key="search_input")
    with col2:
        st.write("") 
        st.write("") 
        btn_search = st.button("조회", type="primary")

    if btn_search or search_name:
        # DB 조회
        df_cust = con.execute("SELECT * FROM Customer WHERE name = ?", [search_name]).df()

        if not df_cust.empty:
            # 고객 존재
            cust_info = df_cust.iloc[0]
            st.success(f"✅ **{cust_info['name']}** 님 (ID: {cust_info['custid']}) 환영합니다!")
            st.info(f"📍 주소: {cust_info['address']} | 📞 전화: {cust_info['phone']}")
            
            # ** 중요: 주문 탭에서 쓰기 위해 세션에 저장 **
            st.session_state.selected_custid = int(cust_info['custid'])
            st.session_state.selected_name = cust_info['name']
            
            st.divider()
            st.subheader("📖 구매 내역")
            history_sql = """
                SELECT b.bookname as 도서명, o.saleprice as 구매가격, o.orderdate as 구매일자
                FROM Orders o
                JOIN Book b ON o.bookid = b.bookid
                WHERE o.custid = ?
                ORDER BY o.orderdate DESC
            """
            df_history = con.execute(history_sql, [cust_info['custid']]).df()
            
            if not df_history.empty:
                st.dataframe(df_history, use_container_width=True, hide_index=True)
            else:
                st.write("구매 내역이 없습니다.")
                
        else:
            # 고객 없음 -> 신규 등록
            st.warning(f"'{search_name}' 고객님은 등록되지 않았습니다.")
            with st.expander("🆕 신규 고객 등록하기", expanded=True):
                with st.form("register_form"):
                    new_addr = st.text_input("주소")
                    new_phone = st.text_input("전화번호")
                    submit_reg = st.form_submit_button("신규 등록")
                    
                    if submit_reg:
                        # ID 자동 생성 (MAX + 1)
                        max_id = con.execute("SELECT MAX(custid) FROM Customer").fetchone()[0]
                        new_id = 1 if max_id is None else max_id + 1
                        
                        con.execute("INSERT INTO Customer VALUES (?, ?, ?, ?)", 
                                    [new_id, search_name, new_addr, new_phone])
                        
                        st.success(f"{search_name}님 등록 완료!")
                        # 자동 로그인 처리
                        st.session_state.selected_custid = new_id
                        st.session_state.selected_name = search_name
                        st.rerun()

# --- [Tab 2] 주문 입력 ---
with tab2:
    st.header("신규 주문")
    
    # 고객 선택 여부 확인
    if st.session_state.selected_custid is None:
        st.warning("👈 '고객 조회' 탭에서 먼저 고객을 조회해주세요.")
    else:
        st.success(f"👤 주문자: **{st.session_state.selected_name}**")
        
        # 책 목록 가져오기
        books = con.execute("SELECT bookid, bookname, price FROM Book").fetchall()
        # 셀렉트박스용 딕셔너리 생성 {"책제목 (가격)": [bookid, price]}
        book_options = {f"{b[1]} ({b[2]:,}원)": b for b in books}
        
        selected_key = st.selectbox("구매할 도서 선택", list(book_options.keys()))
        selected_book_info = book_options[selected_key] # [bookid, name, price]
        
        # 가격 입력 (기본값은 정가)
        input_price = st.number_input("판매 가격", value=selected_book_info[2], step=100)
        
        if st.button("결제 및 주문 저장", type="primary"):
            # 주문 번호 생성
            max_oid = con.execute("SELECT MAX(orderid) FROM Orders").fetchone()[0]
            new_oid = 1 if max_oid is None else max_oid + 1
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Insert 실행
            con.execute("INSERT INTO Orders VALUES (?, ?, ?, ?, ?)", 
                        [new_oid, st.session_state.selected_custid, selected_book_info[0], input_price, today])
            
            st.balloons()
            st.success(f"'{selected_book_info[1]}' 주문이 완료되었습니다!")

# --- [Tab 3] 현황판 ---
with tab3:
    st.header("📊 관리자 현황판")
    if st.button("새로고침"):
        st.rerun()
        
    # 통계 지표
    total_sales = con.execute("SELECT SUM(saleprice) FROM Orders").fetchone()[0]
    total_count = con.execute("SELECT COUNT(*) FROM Orders").fetchone()[0]
    
    col1, col2 = st.columns(2)
    col1.metric("총 매출액", f"{total_sales or 0:,}원")
    col2.metric("총 판매량", f"{total_count}권")
    
    st.divider()
    st.subheader("최근 거래 내역 (10건)")
    
    recent_sql = """
        SELECT o.orderdate as 날짜, c.name as 고객명, b.bookname as 도서명, o.saleprice as 판매가
        FROM Orders o
        JOIN Customer c ON o.custid = c.custid
        JOIN Book b ON o.bookid = b.bookid
        ORDER BY o.orderid DESC
        LIMIT 10
    """
    df_recent = con.execute(recent_sql).df()
    st.dataframe(df_recent, use_container_width=True, hide_index=True)