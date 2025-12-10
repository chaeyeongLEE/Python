import streamlit as st
import pandas as pd
import time
import json
from io import BytesIO
from datetime import datetime
from types import SimpleNamespace  

st.set_page_config(page_title="Admin (Mock)", layout="wide")
status_msg = st.empty()

# 새로고침 (캐시만 초기화)
def refresh_data():
    status_msg.info("새로 불러오는 중입니다.")
    st.cache_data.clear()
    time.sleep(0.3)
    st.rerun()


# DB 조회 함수 대신 더미 데이터 반환 (캐싱, 10분 TTL)
@st.cache_data(ttl=600)
def fetch_members():
    # 원래는 DB(SessionLocal)에서 Member 조회 → 더미 리스트로 대체
    dummy_members = [
        SimpleNamespace(
            id=1,
            email="demo1@example.com",
            name="홍길동",
            phone="010-1234-5678",
            ssn="900101-1234567",
            address="서울특별시 어딘가 1-1",
            created_at=datetime(2025, 11, 1, 10, 0, 0),
        ),
        SimpleNamespace(
            id=2,
            email="demo2@example.com",
            name="김철수",
            phone="010-2222-3333",
            ssn="910202-2345678",
            address="경기도 어딘가 2-2",
            created_at=datetime(2025, 11, 2, 12, 30, 0),
        ),
    ]
    return dummy_members


@st.cache_data(ttl=600)
def fetch_submissions():
    # 원래는 DB에서 Submission 조회 → 더미 리스트로 대체
    dummy_subs = [
        SimpleNamespace(
            id=1,
            member_email="demo1@example.com",
            intention="소송 참여 희망",
            address="서울특별시 어딘가 1-1",
            email="demo1@example.com",
            franchise="배달의민족",
            backup_phone="010-0000-0000",
            coupon_used=True,
            agree_privacy=True,
            confirm_info=True,
            stores=json.dumps(
                [
                    {"name": "서울 1호점", "period": "2020-01 ~ 2023-01"},
                    {"name": "서울 2호점", "period": "2021-05 ~ 2024-01"},
                ]
            ),
            applicants=json.dumps(
                [
                    {
                        "name": "홍길동",
                        "phone": "010-1234-5678",
                        "ssn": "900101-1234567",
                        "address": "서울특별시 어딘가 1-1",
                    }
                ]
            ),
            created_at=datetime(2025, 11, 3, 9, 0, 0),
            status="APPLIED",
            litigation="배민 가맹점 수수료 소송",
        ),
        SimpleNamespace(
            id=2,
            member_email="demo2@example.com",
            intention="관심 있음",
            address="경기도 어딘가 2-2",
            email="demo2@example.com",
            franchise="쿠팡이츠",
            backup_phone="010-9999-8888",
            coupon_used=False,
            agree_privacy=True,
            confirm_info=True,
            stores=json.dumps(
                [
                    {"name": "경기 1호점", "period": "2019-03 ~ 2022-12"},
                ]
            ),
            applicants=json.dumps(
                [
                    {
                        "name": "김철수",
                        "phone": "010-2222-3333",
                        "ssn": "910202-2345678",
                        "address": "경기도 어딘가 2-2",
                    }
                ]
            ),
            created_at=datetime(2025, 11, 5, 15, 30, 0),
            status="UNDER_REVIEW",
            litigation="쿠팡이츠 가맹점 수수료 소송",
        ),
    ]
    return dummy_subs


# 엑셀 변환 함수 (원본 그대로)
def to_excel_bytes(df: pd.DataFrame) -> bytes:
    export_df = df.copy()

    if "가입일" in export_df.columns:
        export_df["가입일"] = pd.to_datetime(export_df["가입일"]).dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    if "접수일시" in export_df.columns:
        export_df["접수일시"] = pd.to_datetime(export_df["접수일시"]).dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="data")

        ws = writer.sheets["data"]
        for col in ws.columns:
            max_len = max(len(str(c.value)) if c.value is not None else 0 for c in col)
            ws.column_dimensions[col[0].column_letter].width = max(
                12, min(max_len + 2, 40)
            )

    return buffer.getvalue()


# 포맷터: 신청인 / 점포 (원본 그대로)
def format_applicants(v):
    if v is None:
        return ""
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except Exception:
            return v

    if isinstance(v, list):
        parts = []
        for a in v:
            if not isinstance(a, dict):
                continue

            name = a.get("name", "")
            phone = a.get("phone", "")
            ssn = a.get("ssn", "")
            address = a.get("address", "")

            inside = []
            if phone:
                inside.append(phone)
            if ssn:
                inside.append(ssn)
            if address:
                inside.append(address)

            inside_text = ", ".join(inside)

            if inside_text:
                parts.append(f"{name}({inside_text})")
            else:
                parts.append(name)

        return ", ".join([p for p in parts if p])

    return str(v)


def format_stores(v):
    if v is None:
        return ""
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except Exception:
            return v
    if isinstance(v, list):
        parts = []
        for s in v:
            if not isinstance(s, dict):
                continue
            name = s.get("name", "")
            period = s.get("period", "")
            parts.append(f"{name}({period})" if period else name)
        return ", ".join([p for p in parts if p])
    return str(v)


# 상태 :: 한글 DB Enum 매핑 (원본 그대로)
STATUS_KR_TO_DB = {
    "접수완료": "APPLIED",
    "검토중": "UNDER_REVIEW",
    "검토완료": "REVIEW_DONE",
    "소송진행": "LAWSUIT_IN_PROGRESS",
    "종결": "FINISHED",
    "취소": "CANCELED",
}
STATUS_DB_TO_KR = {v: k for k, v in STATUS_KR_TO_DB.items()}


# 메인 레이아웃
st.title("YK 집단소송 관리자 페이지 (Mock UI)")

tab1, tab2 = st.tabs(["회원명단", "신청명단"])

# 회원명단 (Members) 탭
with tab1:
    col_title, col_refresh = st.columns([1, 0.15])
    with col_title:
        st.subheader("회원 목록)")
    with col_refresh:
        if st.button("새로 불러오기", key="refresh_members"):
            refresh_data()

    members = fetch_members()
    df_members = pd.DataFrame(
        [
            {
                "id": m.id,
                "email": m.email,
                "name": m.name,
                "phone": m.phone,
                "ssn": m.ssn,
                "address": getattr(m, "address", None),
                "created_at": m.created_at,
            }
            for m in members
        ]
    )

    q = st.text_input("검색 (email, name)", "")
    if q:
        df_members = df_members[
            df_members["email"].str.contains(q, case=False, na=False)
            | df_members["name"].str.contains(q, case=False, na=False)
        ]

    MEMBER_LABELS = {
        "id": "ID",
        "email": "이메일",
        "name": "이름",
        "phone": "휴대폰",
        "ssn": "주민번호",
        "address": "주소",
        "created_at": "가입일",
    }
    df_members_view = df_members.rename(columns=MEMBER_LABELS)

    # 명단 버전 관리 목적 :: 엑셀 파일명에 날짜/시간 붙이기 (YYYYMMDD-HHMM)
    now_str = datetime.now().strftime("%Y%m%d-%H%M")

    col_dl, _ = st.columns(2)
    with col_dl:
        st.download_button(
            "⭳ 회원명단 Excel 다운로드",
            data=to_excel_bytes(df_members_view),
            file_name=f"{now_str}_회원목록.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.dataframe(df_members_view, use_container_width=True, height=420)

    st.markdown("---")
    st.subheader("회원 상세")

    selected = st.selectbox(
        "회원 선택 (이름)",
        df_members["name"].tolist() if not df_members.empty else [],
    )

    if selected:
        m = next((x for x in members if x.name == selected), None)
        if m:
            st.json(
                {
                    "ID": m.id,
                    "이메일": m.email,
                    "이름": m.name,
                    "휴대폰": m.phone,
                    "주민번호": m.ssn,
                    "주소": getattr(m, "address", None),
                    "가입일": str(m.created_at),
                }
            )


# 신청명단(Submissions) 탭
with tab2:
    col_title, col_refresh = st.columns([1, 0.15])
    with col_title:
        st.subheader("제출 목록 (더미 데이터)")
    with col_refresh:
        if st.button("새로 불러오기", key="refresh_submissions"):
            refresh_data()

    subs = fetch_submissions()
    df_subs = pd.DataFrame(
        [
            {
                "id": s.id,
                "member_email": s.member_email,
                "intention": s.intention,
                "address": s.address,
                "email": s.email,
                "franchise": s.franchise,
                "backup_phone": s.backup_phone,
                "coupon_used": s.coupon_used,
                "agree_privacy": s.agree_privacy,
                "confirm_info": s.confirm_info,
                "stores": s.stores,
                "applicants": s.applicants,
                "created_at": s.created_at,
                "status": s.status,
                "litigation": s.litigation,
            }
            for s in subs
        ]
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        email_filter = st.text_input("회원 이메일 검색", "")
    with col2:
        litigation_filter = st.text_input("소송별 검색", "")
    with col3:
        franchise_filter = st.text_input("프랜차이즈별 검색", "")

    if email_filter:
        df_subs = df_subs[
            df_subs["member_email"].str.contains(email_filter, case=False, na=False)
        ]
    if litigation_filter:
        df_subs = df_subs[
            df_subs["litigation"]
            .astype(str)
            .str.contains(litigation_filter, case=False, na=False)
        ]
    if franchise_filter:
        df_subs = df_subs[
            df_subs["franchise"]
            .astype(str)
            .str.contains(franchise_filter, case=False, na=False)
        ]

    if "applicants" in df_subs.columns:
        df_subs["applicants"] = df_subs["applicants"].apply(format_applicants)
    if "stores" in df_subs.columns:
        df_subs["stores"] = df_subs["stores"].apply(format_stores)

    SUB_LABELS = {
        "id": "ID",
        "member_email": "회원이메일",
        "intention": "소송참여 희망 여부",
        "address": "주소",
        "email": "이메일",
        "franchise": "프랜차이즈명",
        "backup_phone": "비상연락처",
        "coupon_used": "쿠폰사용여부",
        "agree_privacy": "개인정보동의",
        "confirm_info": "회원가입동의",
        "stores": "점포/운영정보",
        "applicants": "신청인",
        "created_at": "접수일시",
        "status": "상태",
        "litigation": "사건",
    }

    df_subs_view = df_subs.rename(columns=SUB_LABELS)

    now_str = datetime.now().strftime("%Y%m%d-%H%M")
    col_dl, col_count = st.columns([1, 0.5])
    total_applicants = 0

    # 전체 신청인수
    for s in subs:
        try:
            apps = s.applicants
            if isinstance(apps, str):
                apps = json.loads(apps)

            if isinstance(apps, list):
                total_applicants += len(apps)
        except Exception:
            pass

    with col_dl:
        st.download_button(
            "⭳ 신청명단 Excel 다운로드",
            data=to_excel_bytes(df_subs_view),
            file_name=f"{now_str}_신청명단.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with col_count:
        st.info(f"전체 신청인 수: **{total_applicants}명**")

    st.dataframe(df_subs_view, use_container_width=True, height=420)

    st.markdown("---")
    st.subheader("제출 상세")

    selected_email = st.selectbox(
        "신청자 이메일 선택",
        df_subs["email"].tolist() if not df_subs.empty else [],
    )

    if selected_email:
        s = next((x for x in subs if x.email == selected_email), None)

        if s:
            col_detail, col_edit = st.columns([1, 1])

            with col_detail:
                st.markdown("**현재 신청 정보 (더미)**")
                st.json(
                    {
                        "ID": s.id,
                        "회원이메일": s.member_email,
                        "의뢰의도": s.intention,
                        "주소": s.address,
                        "이메일": s.email,
                        "프랜차이즈명": s.franchise,
                        "비상연락처": s.backup_phone,
                        "쿠폰사용여부": s.coupon_used,
                        "개인정보동의": s.agree_privacy,
                        "회원가입동의": s.confirm_info,
                        "점포/운영정보": s.stores,
                        "신청인": s.applicants,
                        "사건": s.litigation,
                        "상태(원본 Enum)": s.status,
                        "접수일시": str(s.created_at),
                    }
                )

            # 제출 정보 수정
            with col_edit:
                st.markdown("**제출 정보 수정 (UI 데모용, 저장 안 됨)**")

                current_status_kr = STATUS_DB_TO_KR.get(s.status, "접수완료")
                status_options = list(STATUS_KR_TO_DB.keys())

                new_status_kr = st.selectbox(
                    "상태",
                    status_options,
                    index=status_options.index(current_status_kr),
                    key=f"status_{s.id}",
                )

                new_litigation = st.text_input(
                    "사건",
                    value=s.litigation or "",
                    key=f"litigation_{s.id}",
                )

                new_franchise = st.text_input(
                    "프랜차이즈명",
                    value=s.franchise or "",
                    key=f"franchise_{s.id}",
                )

                new_intention = st.text_input(
                    "소송참여 희망 여부",
                    value=s.intention or "",
                    key=f"intention_{s.id}",
                )

                new_backup_phone = st.text_input(
                    "비상연락처",
                    value=s.backup_phone or "",
                    key=f"backup_{s.id}",
                )

                new_address = st.text_input(
                    "주소",
                    value=s.address or "",
                    key=f"address_{s.id}",
                )

               if st.button("⭳ 수정 사항 저장", key=f"save_{s.id}"):
                    st.warning("실패")
    st.markdown("---")
    st.subheader("일별 접수 수")

    if not df_subs.empty:
        daily = df_subs.copy()
        daily["date"] = pd.to_datetime(daily["created_at"]).dt.date
        daily_counts = (
            daily.groupby("date")
            .size()
            .reset_index(name="count")
            .sort_values("date")
        )

        st.line_chart(daily_counts.set_index("date"))
        st.dataframe(daily_counts, use_container_width=True)
    else:
        st.info("제출 데이터가 없습니다.")
