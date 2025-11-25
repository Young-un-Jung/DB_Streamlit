import streamlit as st
import duckdb
import os
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="DuckDB 뷰어", layout="wide")
st.title("Madang_DB 조회 (GitHub 연동)")

# 2. DB 연결 (메모리 모드)
# DuckDB 연결을 세션 상태에 저장하여 새로고침 시 데이터가 유지되도록 처리 (Streamlit 세션이 살아있는 동안)
if "con" not in st.session_state:
    st.session_state.con = duckdb.connect(database=':memory:')
con = st.session_state.con

# 3. GitHub에 같이 올린 'init.sql' 파일 자동 실행
sql_file_path = "demo_madang_init.sql"  # 같은 폴더에 있는 파일명

# Streamlit 앱이 시작될 때마다 초기화 스크립트 실행 (세션마다 DB 초기화)
if os.path.exists(sql_file_path):
    # 단, Streamlit이 재실행될 때마다 DB가 초기화되는 것을 막기 위해 세션 상태 사용
    if 'db_initialized' not in st.session_state:
        try:
            # 파일 읽기
            with open(sql_file_path, "r", encoding="utf-8") as f:
                init_script = f.read()
            
            # DuckDB에서 실행
            con.sql(init_script)
            
            # 초기화 성공 플래그 설정
            st.session_state.db_initialized = True
            
            # 성공 메시지 (사이드바에 작게 표시)
            st.sidebar.success(f"✅ '{sql_file_path}' 로드 완료!")
            
        except Exception as e:
            st.error(f"SQL 파일 실행 중 오류 발생: {e}")
            st.session_state.db_initialized = False # 오류 발생 시에도 플래그 설정
else:
    st.warning(f"⚠️ '{sql_file_path}' 파일을 찾을 수 없습니다. GitHub에 파일을 같이 올려주세요.")


# 4. 사이드바에 현재 테이블 목록 표시
if 'db_initialized' in st.session_state and st.session_state.db_initialized:
    try:
        tables = con.sql("SHOW TABLES").df()
        st.sidebar.write("📋 **테이블 목록**")
        st.sidebar.dataframe(tables, hide_index=True)
    except:
        st.sidebar.info("DB 초기화 후 테이블 목록을 가져올 수 없습니다.")


# 5. 데이터 조회 화면
st.divider()

# 기본 쿼리 설정
try:
    first_table = con.sql("SHOW TABLES").fetchone()[0]
    default_query = f"SELECT * FROM {first_table} LIMIT 20;"
except:
    default_query = "SELECT 'DB가 초기화되지 않았거나 테이블이 없습니다.'"


user_query = st.text_area("SQL 쿼리문 입력", value=default_query, height=100)

if st.button("🔍 실행 (Run)", type="primary"):
    try:
        # 쿼리 실행
        result_set = con.sql(user_query)
        
        # DML(INSERT, UPDATE, DELETE) 쿼리인지, SELECT 쿼리인지 구분
        if result_set is None:
            # DML 쿼리는 결과를 반환하지 않으므로 성공 메시지만 출력
            st.success("쿼리가 성공적으로 실행되었습니다. (데이터 조작 또는 스키마 변경)")
            
            # 테이블 목록을 다시 보여주어 변경사항 반영 (예: 새로운 테이블 생성 시)
            try:
                tables = con.sql("SHOW TABLES").df()
                st.sidebar.write("📋 **테이블 목록 (업데이트)**")
                st.sidebar.dataframe(tables, hide_index=True)
            except:
                 st.sidebar.info("테이블 목록을 다시 가져오는 중 오류 발생.")
                 
        else:
            # SELECT 쿼리는 결과를 반환하므로 DataFrame으로 변환하여 출력
            df = result_set.df()
            st.success(f"조회 결과: {len(df)}건")
            st.dataframe(df, use_container_width=True) # 모바일 너비에 맞춤

    except Exception as e:
        # 쿼리 실행 자체에서 발생한 오류 (예: 문법 오류, 컬럼명 오류 등)
        st.error(f"쿼리 실행 오류: {e}")