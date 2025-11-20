import streamlit as st
import duckdb
import os

# 1. 페이지 설정
st.set_page_config(page_title="DuckDB 뷰어", layout="wide")
st.title("📱 Madang_DB 조회 (GitHub 연동)")

# 2. DB 연결 (메모리 모드)
con = duckdb.connect(database=':memory:')

# 3. GitHub에 같이 올린 'init.sql' 파일 자동 실행
sql_file_path = "demo_madang_init.sql"  # 같은 폴더에 있는 파일명

if os.path.exists(sql_file_path):
    try:
        # 파일 읽기
        with open(sql_file_path, "r", encoding="utf-8") as f:
            init_script = f.read()
        
        # DuckDB에서 실행
        con.sql(init_script)
        
        # 성공 메시지 (사이드바에 작게 표시)
        st.sidebar.success(f"✅ '{sql_file_path}' 로드 완료!")
        
        # 현재 테이블 목록 사이드바에 표시
        tables = con.sql("SHOW TABLES").df()
        st.sidebar.write("📋 **테이블 목록**")
        st.sidebar.dataframe(tables, hide_index=True)
        
    except Exception as e:
        st.error(f"SQL 파일 실행 중 오류 발생: {e}")
else:
    st.warning(f"⚠️ '{sql_file_path}' 파일을 찾을 수 없습니다. GitHub에 파일을 같이 올려주세요.")

# 4. 데이터 조회 화면
st.divider()

# 기본적으로 첫 번째 테이블의 데이터를 보여줌 (편의성)
try:
    first_table = con.sql("SHOW TABLES").fetchone()[0]
    default_query = f"SELECT * FROM {first_table} LIMIT 20;"
except:
    default_query = "SELECT 1;"

user_query = st.text_area("SQL 쿼리문 입력", value=default_query, height=100)

if st.button("🔍 실행 (Run)", type="primary"):
    try:
        df = con.sql(user_query).df()
        st.dataframe(df, use_container_width=True) # 모바일 너비에 맞춤
    except Exception as e:
        st.error(f"쿼리 오류: {e}")