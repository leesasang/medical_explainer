import re
import streamlit as st
from core import Person, LabInput, TEST_CATEGORIES, TEST_GROUPS, LAB_META, DISPLAY_NAMES_KO, UNITS_DEFAULT, interpret_selected_items, make_report, create_pdf_bytes

st.set_page_config(page_title="검사 결과 쉬운 설명기", layout="wide")

STATUS_BG = {"normal":"#ECFDF5","borderline":"#FEF3C7","low":"#DBEAFE","high":"#FEE2E2","critical":"#FECACA","unknown":"#F3F4F6"}
STATUS_BORDER = {"normal":"#10B981","borderline":"#F59E0B","low":"#3B82F6","high":"#EF4444","critical":"#DC2626","unknown":"#9CA3AF"}

st.markdown("""
<style>
.metric-card {
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border: 2px solid #E5E7EB;
}
.group-title {
    font-size: 1.15rem;
    font-weight: 700;
    margin-top: 0.8rem;
    margin-bottom: 0.5rem;
}
.small-muted {
    color: #374151;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

for k in ("results","report","person"):
    if k not in st.session_state:
        st.session_state[k] = None

def get_default_ref(key, sex):
    meta = LAB_META.get(key, {})
    if sex == "male" and "default_ref_male" in meta:
        return meta["default_ref_male"]
    if sex == "female" and "default_ref_female" in meta:
        return meta["default_ref_female"]
    return meta.get("default_ref", {"low": None, "high": None})

def parse_bp(text):
    if not text:
        return None, "혈압 입력값이 없습니다."
    m = re.match(r"^\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$", text)
    if not m:
        return None, "혈압은 120/80 형식으로 입력하세요."
    sbp = float(m.group(1)); dbp = float(m.group(2))
    if sbp <= dbp:
        return None, "혈압 입력을 다시 확인하세요. 수축기혈압은 이완기혈압보다 커야 합니다."
    if not (50 <= sbp <= 260 and 30 <= dbp <= 180):
        return None, "혈압 값이 일반적인 입력 범위를 벗어났습니다."
    return (sbp, dbp), None

def completion_rate(labs, keys):
    filled = 0
    for key in keys:
        li = labs.get(key)
        if li and li.value not in (None, "", "미입력"):
            filled += 1
    total = len(keys)
    return filled, total, (filled / total * 100 if total else 0)

def render_status_card(result):
    bg = STATUS_BG.get(result.status, "#F3F4F6")
    border = STATUS_BORDER.get(result.status, "#9CA3AF")
    value_str = f"{result.value} {result.unit}".strip() if result.value is not None else "입력값 없음"
    st.markdown(f"""
        <div class="metric-card" style="background:{bg}; border-color:{border}; color:#111827;">
            <div style="font-weight:700; color:#111827;">{result.name_ko}</div>
            <div class="small-muted" style="color:#374151;">입력값: {value_str}</div>
            <div style="margin-top:6px; font-weight:600; color:#111827;">{result.short}</div>
        </div>
    """, unsafe_allow_html=True)

st.title("🩺 검사 결과 쉬운 설명기")
st.caption("한 번에 하나의 검사지 종류만 선택해서 입력하고, 해석 결과와 PDF 리포트를 확인할 수 있습니다. (진단/처방 아님)")

with st.sidebar:
    st.header("기본 정보")
    age = st.number_input("나이", min_value=1, max_value=120, value=25, step=1)
    sex = st.selectbox("성별", options=[("male", "남성"), ("female", "여성")], format_func=lambda x: x[1])[0]
    st.divider()
    selected_category = st.selectbox("검사지를 선택하세요", list(TEST_CATEGORIES.keys()))
    st.caption("현재 버전은 한 번에 하나의 검사지 종류만 선택할 수 있습니다.")
    allow_custom_ref = st.toggle("참고치 수정 허용", value=False)
    st.caption("단위는 고정이며, 참고치 수정은 펼침 영역에서만 가능합니다.")

person = Person(age=int(age), sex=sex)
selected_keys = TEST_CATEGORIES[selected_category]
group_map = TEST_GROUPS[selected_category]

temp_labs = {}
st.subheader(f"{selected_category} 결과 입력")
st.write("카드형으로 정리했으며, 단위는 고정입니다. 참고치 수정은 필요한 경우에만 펼쳐서 바꾸세요.")

for group_name, group_keys in group_map.items():
    st.markdown(f'<div class="group-title">{group_name}</div>', unsafe_allow_html=True)
    cols = st.columns(2, gap="large")
    for idx, key in enumerate(group_keys):
        meta = LAB_META[key]
        name = DISPLAY_NAMES_KO.get(key, key)
        unit = UNITS_DEFAULT.get(key, "")
        default_ref = get_default_ref(key, sex)
        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                if unit:
                    st.caption(f"단위: {unit}")
                if meta["input_type"] == "numeric":
                    value = st.number_input(
                        f"{name} 수치",
                        min_value=float(meta.get("min", 0.0)),
                        max_value=float(meta.get("max", 100000.0)),
                        value=None,
                        step=float(meta.get("step", 1.0)),
                        key=f"v_{selected_category}_{key}",
                        placeholder="값 입력"
                    )
                    ref_low = default_ref.get("low")
                    ref_high = default_ref.get("high")
                    if ref_low is not None or ref_high is not None:
                        st.caption(f"기본 참고치: {ref_low if ref_low is not None else '-'} ~ {ref_high if ref_high is not None else '-'}")
                    if allow_custom_ref and key != "bp":
                        with st.expander("참고치 수정"):
                            c1, c2 = st.columns(2)
                            with c1:
                                lo = st.number_input("참고치 하한", value=float(ref_low) if ref_low is not None else None, step=float(meta.get("step", 1.0)), key=f"lo_{selected_category}_{key}")
                            with c2:
                                hi = st.number_input("참고치 상한", value=float(ref_high) if ref_high is not None else None, step=float(meta.get("step", 1.0)), key=f"hi_{selected_category}_{key}")
                            ref_low = lo
                            ref_high = hi
                    temp_labs[key] = LabInput(value=value, ref_low=ref_low, ref_high=ref_high, unit=unit)
                elif meta["input_type"] == "bp_text":
                    bp_text = st.text_input("혈압 입력", key=f"v_{selected_category}_{key}", placeholder=meta.get("placeholder", "120/80"))
                    parsed, err = parse_bp(bp_text) if bp_text else (None, None)
                    if err and bp_text:
                        st.error(err)
                    st.caption("예: 120/80")
                    temp_labs[key] = LabInput(value=parsed, unit=unit)
                else:
                    value = st.selectbox(f"{name} 결과", options=meta["choices"], key=f"v_{selected_category}_{key}")
                    temp_labs[key] = LabInput(value=None if value == "미입력" else value, unit="")
                st.caption(f"입력 방식: {meta['input_type']}")

filled, total, pct = completion_rate(temp_labs, selected_keys)
st.divider()
st.subheader("입력 완료율")
st.progress(int(pct))
st.caption(f"{filled} / {total} 항목 입력 완료 ({pct:.0f}%)")

st.divider()
c1, c2 = st.columns(2)
with c1:
    run = st.button("해석 생성", type="primary", use_container_width=True)
with c2:
    make_pdf = st.button("PDF 변환 준비", use_container_width=True)

if run:
    bp_li = temp_labs.get("bp")
    if "bp" in selected_keys and bp_li and bp_li.value is None:
        st.error("혈압 입력 형식을 확인하세요. 예: 120/80")
    else:
        st.session_state.results = interpret_selected_items(person, temp_labs, selected_keys)
        st.session_state.report = make_report(person, st.session_state.results)
        st.session_state.person = person

if st.session_state.results:
    st.subheader("이상치 요약 카드")
    abnormal = [r for r in st.session_state.results if r.status in {"borderline", "low", "high", "critical"}]
    normal = [r for r in st.session_state.results if r.status == "normal"]
    target = abnormal if abnormal else normal[:4]
    cols = st.columns(2, gap="large")
    for idx, r in enumerate(target):
        with cols[idx % 2]:
            render_status_card(r)

    st.divider()
    st.subheader("항목별 상세 결과")
    emoji = {"critical":"🛑","high":"🔶","borderline":"🟡","low":"🔵","normal":"✅","unknown":"❔"}
    for r in st.session_state.results:
        with st.expander(f"{emoji.get(r.status, '❔')} {r.name_ko}"):
            value_str = f"{r.value} {r.unit}".strip() if r.value is not None else "입력값 없음"
            st.markdown(f"**입력값:** {value_str}")
            st.markdown(f"**판정:** `{r.status}`")
            st.markdown(f"**한 줄 요약:** {r.short}")
            st.markdown(f"**쉬운 설명:** {r.easy_explain}")
            if r.possible_causes:
                st.markdown("**가능한 원인(일반):**")
                for c in r.possible_causes:
                    st.markdown(f"- {c}")
            if r.next_steps:
                st.markdown("**다음 행동(일반):**")
                for s in r.next_steps:
                    st.markdown(f"- {s}")
            if r.warnings:
                st.markdown("**주의:**")
                for w in r.warnings:
                    st.markdown(f"- {w}")
            if r.evidence:
                st.markdown("**근거/기준:**")
                for e in r.evidence:
                    st.markdown(f"- {e}")

if make_pdf:
    if st.session_state.results and st.session_state.report and st.session_state.person:
        pdf_bytes = create_pdf_bytes(st.session_state.person, st.session_state.results, st.session_state.report)
        st.success("PDF 변환이 준비되었습니다. 아래 버튼으로 다운로드하세요.")
        st.download_button("PDF 리포트 다운로드", data=pdf_bytes, file_name="검사결과_해석_리포트.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.warning("먼저 해석 생성을 눌러 결과를 만든 뒤 PDF 변환을 진행하세요.")

if st.session_state.report:
    st.subheader("면책/주의")
    for d in st.session_state.report["disclaimer"]:
        st.markdown(f"- {d}")
