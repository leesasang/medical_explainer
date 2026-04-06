from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

def make_report(person, results):
    critical=[r for r in results if r.status=="critical"]; high=[r for r in results if r.status=="high"]; borderline=[r for r in results if r.status in ("borderline","low")]; normal=[r for r in results if r.status=="normal"]
    summary=[]
    if critical:
        summary.append("즉시 확인이 필요한 신호가 있을 수 있습니다.")
        for r in critical: summary.append(f"- {r.name_ko}: {r.short}")
    if high:
        summary.append("높은 범주로 분류된 항목")
        for r in high: summary.append(f"- {r.name_ko}: {r.short}")
    if borderline:
        summary.append("경계/낮음 범주 항목")
        for r in borderline: summary.append(f"- {r.name_ko}: {r.short}")
    if normal and not (critical or high or borderline):
        summary.append("입력된 항목 기준으로 크게 벗어난 신호가 없어 보입니다.")
    disclaimer=["이 결과는 진단/처방이 아닌 정보 제공용 설명입니다.","증상이 있거나 수치가 걱정되면 의료진과 상담하세요.","검사기관과 개인 상태에 따라 참고치와 해석이 달라질 수 있습니다."]
    return {"person":{"age":person.age,"sex":person.sex},"summary":summary,"disclaimer":disclaimer}

def create_pdf_bytes(person, results, report):
    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
    styles=getSampleStyleSheet()
    normal=styles["BodyText"]; normal.fontName="HYSMyeongJo-Medium"; normal.fontSize=10
    title=styles["Title"]; title.fontName="HYSMyeongJo-Medium"; title.fontSize=18
    h2=styles["Heading2"]; h2.fontName="HYSMyeongJo-Medium"; h2.fontSize=13
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=18*mm,bottomMargin=18*mm)
    story=[]
    sex_ko="남성" if person.sex=="male" else "여성"
    story.append(Paragraph("검사 결과 해석 리포트", title)); story.append(Spacer(1,8))
    story.append(Paragraph(f"기본 정보: 나이 {person.age}세 / 성별 {sex_ko}", normal)); story.append(Spacer(1,10))
    story.append(Paragraph("요약", h2))
    for line in report["summary"]: story.append(Paragraph(line, normal))
    story.append(Spacer(1,10)); story.append(Paragraph("항목별 결과", h2))
    for item in results:
        value_str=f"{item.value} {item.unit}".strip() if item.value is not None else "입력값 없음"
        story.append(Paragraph(f"{item.name_ko} [{item.status}]", normal))
        story.append(Paragraph(f"입력값: {value_str}", normal))
        story.append(Paragraph(f"한 줄 요약: {item.short}", normal))
        story.append(Paragraph(f"설명: {item.easy_explain}", normal))
        if item.next_steps:
            story.append(Paragraph("다음 행동:", normal))
            story.append(ListFlowable([ListItem(Paragraph(s, normal)) for s in item.next_steps], bulletType="bullet"))
        if item.warnings:
            story.append(Paragraph("주의:", normal))
            story.append(ListFlowable([ListItem(Paragraph(w, normal)) for w in item.warnings], bulletType="bullet"))
        if item.evidence:
            story.append(Paragraph("근거/기준:", normal))
            story.append(ListFlowable([ListItem(Paragraph(e, normal)) for e in item.evidence], bulletType="bullet"))
        story.append(Spacer(1,8))
    story.append(Paragraph("면책/주의", h2))
    for d in report["disclaimer"]: story.append(Paragraph(d, normal))
    doc.build(story); return buffer.getvalue()
