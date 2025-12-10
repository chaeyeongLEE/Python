import streamlit as st
import pandas as pd
import json
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Admin Mock UI", layout="wide")

# -------------------------------------------------------
# 더미 데이터
# -------------------------------------------------------
dummy_members = [
    {
        "id": 1,
        "email": "demo1@example.com",
        "name": "홍길동",
        "phone": "010-1234-5678",
        "ssn": "900101-1234567",
        "address": "서울특별시 어딘가 1-1",
        "created_at": datetime(2025, 11, 1, 10, 0, 0),
    },
    {
        "id": 2,
        "email": "demo2@example.com",
        "name": "김철수",
        "phone": "010-2222-3333",
        "ssn": "910202-2345678",
        "address": "경기도 어딘가 2-2",
        "created_at": datetime(2025, 11, 2, 12, 30, 0),
    },
]

dummy_subs = [
    {
        "id": 1,
        "member_email": "demo1@example.com",
        "intention": "소송 참여 희망",
        "address": "서울특별시 어딘가 1-1",
        "email": "demo1@example.com",
        "franchise": "배달의민족",
        "backup_phone": "010-0000-0000",
        "coupon_used": True,
        "agree_privacy": True,
        "confirm_info": True,
        "stores": json.dumps([
            {"name": "서울 1호점", "period": "2020-01 ~ 2023-01"}
        ]),
        "applicants": json.dumps([
            {"name": "홍길동", "phone": "010-1234-5678", "address": "서울특별시 어딘가 1-1"}
        ]),
        "created_at": datetime(2025, 11, 3, 9, 0, 0),
        "status": "APPLIED",
        "litigation": "배민 수수료 소송",
    },
    {
        "id": 2,
        "member_email": "demo2@example.com",
        "intention": "관심 있음",
        "address": "경기도 어딘가 2-2",
        "email": "demo2@example.com",
        "franchise": "쿠팡이츠",
        "backup_phone": "010-9999-8888",
        "coupon_used": False,
        "agree_privacy": True,
        "confirm_info": True,
        "stores": json.dumps([
            {"name": "경기 1호점", "period": "2019-03 ~ 2022-12"}
        ]),
        "applicants": json.dumps([
            {"name": "김철수", "phone": "010-2222-3333", "address": "경기도 어딘가 2-2"}
        ]),
        "created_at": datetime(2025, 11, 5, 15, 30, 0),
        "status": "UNDER_REVIEW",
        "litigation": "쿠팡이츠 수수료 소송",
    },
]

# -------------------------------------------------------
# 엑셀 변환
# -------------------------------------------------------
def to_excel_bytes(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue()

# -------------------------------------------------------
# UI 시작
# -------------------------------------------------------
st.title("YK 집단소송 관리자 페이지 (Mock UI - DB 없이 동작)")

tab1, tab2 = st.tabs(["회원명단", "신청명단"])

# -------------------------------------------------------
# 회원명단
# -------------------------------------------------------
with tab1:
    st.subheader("회원 목록")

    df_members = pd.DataFrame(dummy_members)

    q = st.text_input("검색 (email, name)")
    if q:
        df_members = df_members[
            df_members["email"].str.contains(q)
            | df_members["name"].str.contains(q)
        ]

    st.dataframe(df_members, height=400, use_container_width=True)

    st.download_button(
        "회원 목록 다운로드",
        data=to_excel_bytes(df_members),
        file_name="members.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.subheader("회원 상세 보기")
    selected = st.selectbox("회원 선택", df_members["name"])

    detail = df_members[df_members["name"] == selected].iloc[0]
    st.json(detail.to_dict())

# -------------------------------------------------------
# 신청명단
# -------------------------------------------------------
with tab2:
    st.subheader("제출 목록")

    df_subs = pd.DataFrame(dummy_subs)

    # 문자열 JSON → 파싱
    df_subs["stores"] = df_subs["stores"].apply(json.loads)
    df_subs["applicants"] = df_subs["applicants"].apply(json.loads)

    st.dataframe(df_subs, height=400, use_container_width=True)

    st.download_button(
        "신청명단 다운로드",
        data=to_excel_bytes(df_subs),
        file_name="submissions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.subheader("제출 상세")
    selected_email = st.selectbox("이메일 선택", df_subs["email"])

    detail = df_subs[df_subs["email"] == selected_email].iloc[0]
    st.json(detail.to_dict())
