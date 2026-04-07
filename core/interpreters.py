from .models import LabInput, ItemResult
from .catalog import DISPLAY_NAMES_KO, UNITS_DEFAULT, LAB_META

def fmt(v):
    if v is None: return "-"
    if isinstance(v, float): return f"{v:.3f}".rstrip("0").rstrip(".")
    return str(v)

def urgency_label(level):
    return {"routine":"일반 추적","recheck":"재검 권고","consult":"상담 권고","urgent":"빠른 확인 권고"}.get(level, "일반 추적")

def default_ref_for(key, person):
    meta = LAB_META.get(key, {})
    if person.sex == "male" and "default_ref_male" in meta: return meta["default_ref_male"]
    if person.sex == "female" and "default_ref_female" in meta: return meta["default_ref_female"]
    return meta.get("default_ref", {"low": None, "high": None})

def classify_numeric(value, low, high):
    if low is not None and value < low: return "low"
    if high is not None and value > high: return "high"
    if low is None and high is None: return "unknown"
    return "normal"

def build_result(key, value, unit, status, short, explain, causes=None, next_steps=None, warnings=None, evidence=None, urgency="routine"):
    evidence = list(evidence or [])
    evidence.append(f"권장 후속 단계: {urgency_label(urgency)}")
    return ItemResult(key=key, name_ko=DISPLAY_NAMES_KO.get(key, key), value=value, unit=unit, status=status, short=short, easy_explain=explain, possible_causes=causes or [], next_steps=next_steps or [], warnings=warnings or [], evidence=evidence, urgency=urgency)

def missing_result(key):
    return build_result(key, None, UNITS_DEFAULT.get(key, ""), "unknown", "입력값이 없습니다.", "이 항목은 값이 있어야 해석할 수 있습니다.", next_steps=["검사 결과를 입력하세요."])

def interpret_bp(li):
    if not li.value: return missing_result("bp")
    sbp, dbp = li.value
    if sbp >= 180 or dbp >= 120: return build_result("bp", f"{fmt(sbp)}/{fmt(dbp)}", "mmHg", "critical", "혈압이 매우 높습니다.", "즉시 확인이 필요한 고혈압 범주에 해당할 수 있습니다.", next_steps=["증상이 있으면 즉시 진료가 필요할 수 있습니다."], warnings=["혈압은 반복 측정 평균이 중요합니다."], evidence=["일반적인 혈압 범주 기준"], urgency="urgent")
    if sbp >= 140 or dbp >= 90: return build_result("bp", f"{fmt(sbp)}/{fmt(dbp)}", "mmHg", "high", "혈압이 높은 범주입니다.", "반복 측정 시에도 높다면 관리가 필요할 수 있습니다.", next_steps=["가정혈압 추적과 상담을 고려하세요."], warnings=["혈압은 반복 측정 평균이 중요합니다."], evidence=["일반적인 혈압 범주 기준"], urgency="consult")
    if (130 <= sbp <= 139) or (80 <= dbp <= 89) or ((120 <= sbp <= 129) and dbp < 80): return build_result("bp", f"{fmt(sbp)}/{fmt(dbp)}", "mmHg", "borderline", "혈압이 다소 높을 수 있습니다.", "한 번의 측정만으로 단정하기보다는 반복 측정이 중요합니다.", next_steps=["집에서 며칠간 반복 측정해 평균을 보세요."], warnings=["혈압은 반복 측정 평균이 중요합니다."], evidence=["일반적인 혈압 범주 기준"], urgency="recheck")
    return build_result("bp", f"{fmt(sbp)}/{fmt(dbp)}", "mmHg", "normal", "혈압이 일반적인 정상 범주입니다.", "현재 수치는 일반적인 기준에서 크게 벗어나지 않습니다.", next_steps=["정기적으로 추적하세요."], warnings=["혈압은 반복 측정 평균이 중요합니다."], evidence=["일반적인 혈압 범주 기준"])

def interpret_fasting_glucose(person, li):
    if li.value is None: return missing_result("fasting_glucose")
    v=float(li.value); low=li.ref_low if li.ref_low is not None else 70; high=li.ref_high if li.ref_high is not None else 99; evidence=[f"참고치: {fmt(low)} ~ {fmt(high)} {li.unit}"]
    if v >= 200: return build_result("fasting_glucose", v, li.unit, "critical", "공복혈당이 매우 높습니다.", "혈당이 뚜렷하게 상승한 상태로 보입니다.", ["당 대사 이상 가능성"], ["증상이 있거나 수치가 반복되면 빠르게 의료진과 상담하세요."], ["진단을 확정하지 않습니다."], evidence, "urgent")
    if v >= 126: return build_result("fasting_glucose", v, li.unit, "high", "공복혈당이 높게 측정되었습니다.", "공복 상태 혈당이 일반 기준보다 높습니다.", ["당 대사 이상 가능성"], ["재검 또는 추가 검사를 의료진과 상의하세요."], ["진단을 확정하지 않습니다."], evidence, "consult")
    if 100 <= v <= 125: return build_result("fasting_glucose", v, li.unit, "borderline", "공복혈당이 경계 범위일 수 있습니다.", "공복 상태 혈당이 다소 높은 편으로 보입니다.", ["식습관", "운동 부족", "체중 증가"], ["생활습관 조정 후 재검을 고려하세요."], ["진단을 확정하지 않습니다."], evidence, "recheck")
    if v < 70: return build_result("fasting_glucose", v, li.unit, "low", "공복혈당이 낮게 측정되었습니다.", "공복 시간이 길었거나 일시적 영향이 반영되었을 수 있습니다.", ["공복 시간 과도", "컨디션 영향"], ["저혈당 증상이 있으면 의료진과 상담하세요."], ["진단을 확정하지 않습니다."], evidence, "consult")
    return build_result("fasting_glucose", v, li.unit, "normal", "공복혈당이 참고 범위 안에 있습니다.", "현재 수치는 일반적인 참고 범위 안으로 보입니다.", next_steps=["단일 결과보다 추세를 함께 보세요."], warnings=["진단을 확정하지 않습니다."], evidence=evidence)

def interpret_hba1c(person, li):
    if li.value is None: return missing_result("hba1c")
    v=float(li.value); low=li.ref_low if li.ref_low is not None else 4.0; high=li.ref_high if li.ref_high is not None else 5.6; evidence=[f"참고치: {fmt(low)} ~ {fmt(high)} {li.unit}"]
    if v >= 6.5: return build_result("hba1c", v, li.unit, "high", "당화혈색소가 높게 측정되었습니다.", "최근 2~3개월 평균 혈당이 높았을 가능성을 시사할 수 있습니다.", next_steps=["공복혈당과 함께 추가 확인을 고려하세요."], warnings=["진단을 확정하지 않습니다."], evidence=evidence, urgency="consult")
    if 5.7 <= v <= 6.4: return build_result("hba1c", v, li.unit, "borderline", "당화혈색소가 경계 범위일 수 있습니다.", "최근 평균 혈당이 다소 높은 편일 수 있습니다.", next_steps=["생활습관 조정 후 추적 검사를 고려하세요."], warnings=["진단을 확정하지 않습니다."], evidence=evidence, urgency="recheck")
    return build_result("hba1c", v, li.unit, "normal", "당화혈색소가 크게 벗어나지 않습니다.", "현재 수치는 일반적인 참고 범위 안으로 보입니다.", next_steps=["추세를 함께 확인하세요."], warnings=["진단을 확정하지 않습니다."], evidence=evidence)

def interpret_generic_numeric(key, person, li):
    if li.value is None: return missing_result(key)
    v=float(li.value); ref=default_ref_for(key, person); low=li.ref_low if li.ref_low is not None else ref.get("low"); high=li.ref_high if li.ref_high is not None else ref.get("high")
    name=DISPLAY_NAMES_KO.get(key, key); evidence=[f"참고치: {fmt(low)} ~ {fmt(high)} {li.unit}"]; status=classify_numeric(v, low, high)
    if key == "wbc":
        if v < 3.0: return build_result(key, v, li.unit, "high", "백혈구가 뚜렷하게 낮습니다.", "백혈구 수가 낮아 보여 감염 방어와 관련된 평가가 필요할 수 있습니다.", ["약물, 바이러스 감염, 골수 억제 등 다양한 원인 가능"], ["발열, 잦은 감염이 있으면 빠르게 상담을 고려하세요."], ["CBC 단일 항목만으로 원인을 특정할 수 없습니다."], evidence, "consult")
        if v < 4.0: return build_result(key, v, li.unit, "borderline", "백혈구가 낮은 편입니다.", "경미한 감소일 수 있어 증상과 함께 해석하는 것이 좋습니다.", ["일시적 변화 가능성"], ["재검과 임상 증상 확인을 고려하세요."], ["CBC 단일 항목만으로 원인을 특정할 수 없습니다."], evidence, "recheck")
        if v <= 11.0: return build_result(key, v, li.unit, "normal", "백혈구가 일반 범주입니다.", "현재 수치는 일반적인 참고 범위 안으로 보입니다.", next_steps=["추세를 함께 확인하세요."], warnings=["CBC 단일 항목만으로 원인을 특정할 수 없습니다."], evidence=evidence)
        if v <= 15.0: return build_result(key, v, li.unit, "borderline", "백혈구가 약간 높습니다.", "감염, 염증, 스트레스 반응 등과 연관될 수 있습니다.", ["감염", "염증", "스트레스 반응"], ["증상과 함께 재검을 고려하세요."], ["CBC 단일 항목만으로 원인을 특정할 수 없습니다."], evidence, "recheck")
        return build_result(key, v, li.unit, "high", "백혈구가 뚜렷하게 높습니다.", "백혈구 수가 분명히 상승해 있어 임상 맥락 확인이 필요할 수 있습니다.", ["감염", "염증", "약물 반응 등"], ["발열 등 증상이 있거나 지속되면 상담을 고려하세요."], ["CBC 단일 항목만으로 원인을 특정할 수 없습니다."], evidence, "consult")
    if key == "platelet":
        if v < 50: return build_result(key, v, li.unit, "critical", "혈소판이 매우 낮습니다.", "출혈 위험과 연관될 수 있어 빠른 확인이 필요할 수 있습니다.", ["출혈 경향 여부 확인"], ["멍, 코피, 잇몸 출혈이 있으면 빠른 진료를 권합니다."], ["단일 검사만으로 원인을 단정할 수 없습니다."], evidence, "urgent")
        if v < 100: return build_result(key, v, li.unit, "high", "혈소판이 뚜렷하게 낮습니다.", "출혈 경향과 함께 해석이 필요할 수 있습니다.", ["약물, 감염, 면역 반응 등 다양한 원인 가능"], ["증상과 함께 상담을 고려하세요."], ["단일 검사만으로 원인을 단정할 수 없습니다."], evidence, "consult")
        if v < 150: return build_result(key, v, li.unit, "borderline", "혈소판이 약간 낮습니다.", "경미한 감소일 수 있어 반복 여부 확인이 중요합니다.", next_steps=["재검과 임상 맥락 확인을 고려하세요."], warnings=["단일 검사만으로 원인을 단정할 수 없습니다."], evidence=evidence, urgency="recheck")
        if v <= 450: return build_result(key, v, li.unit, "normal", "혈소판이 일반 범주입니다.", "현재 수치는 일반적인 참고 범위 안으로 보입니다.", next_steps=["추세를 함께 확인하세요."], warnings=["단일 검사만으로 원인을 단정할 수 없습니다."], evidence=evidence)
        if v <= 600: return build_result(key, v, li.unit, "borderline", "혈소판이 높습니다.", "염증이나 반응성 변화와 연관될 수 있습니다.", ["염증", "철결핍", "반응성 변화 가능"], ["지속되면 재검을 고려하세요."], ["단일 검사만으로 원인을 단정할 수 없습니다."], evidence, "recheck")
        return build_result(key, v, li.unit, "high", "혈소판이 뚜렷하게 높습니다.", "지속적 상승이라면 원인 평가가 필요할 수 있습니다.", ["염증, 골수 관련 변화 등 다양한 원인 가능"], ["지속되면 상담을 고려하세요."], ["단일 검사만으로 원인을 단정할 수 없습니다."], evidence, "consult")
    if key == "hemoglobin":
        if status == "low": return build_result(key, v, li.unit, "low", "혈색소가 낮게 측정되었습니다.", "빈혈 가능성을 시사할 수 있어 적혈구 및 헤마토크릿과 함께 보는 것이 좋습니다.", ["철결핍, 출혈, 만성질환 등 다양한 원인 가능"], ["피로감, 어지러움이 있으면 상담을 고려하세요."], ["단일 검사만으로 원인을 단정할 수 없습니다."], evidence, "consult" if v < (10.0 if person.sex == "male" else 9.5) else "recheck")
    if key == "hematocrit":
        if status == "low": return build_result(key, v, li.unit, "low", "헤마토크릿이 낮게 측정되었습니다.", "혈액 내 적혈구 비율이 낮아 보이며 혈색소와 함께 해석하는 것이 중요합니다.", next_steps=["혈색소, 적혈구 수치와 함께 확인하세요."], warnings=["단일 검사만으로 원인을 단정할 수 없습니다."], evidence=evidence, urgency="recheck")
    if key == "rbc":
        if status == "low": return build_result(key, v, li.unit, "low", "적혈구 수가 낮게 측정되었습니다.", "빈혈 가능성을 시사할 수 있어 혈색소, 헤마토크릿과 함께 보는 것이 좋습니다.", next_steps=["혈색소, 헤마토크릿과 함께 확인하세요."], warnings=["단일 검사만으로 원인을 단정할 수 없습니다."], evidence=evidence, urgency="recheck")
    if key == "egfr":
        if v < 30: return build_result(key, v, li.unit, "critical", "eGFR이 매우 낮습니다.", "신장 기능 저하 가능성을 강하게 시사할 수 있습니다.", next_steps=["빠른 시일 내 의료진 상담을 권합니다."], warnings=["단일 검사만으로 원인을 단정할 수 없습니다."], evidence=evidence, urgency="urgent")
        if v < 60: return build_result(key, v, li.unit, "high", "eGFR이 낮은 편입니다.", "신장 기능과 관련된 추가 확인이 필요할 수 있습니다.", next_steps=["추가 평가를 의료진과 상의하세요."], warnings=["단일 검사만으로 원인을 단정할 수 없습니다."], evidence=evidence, urgency="consult")
        if v < 90: return build_result(key, v, li.unit, "borderline", "eGFR이 다소 낮을 수 있습니다.", "연령, 체격, 기존 질환과 함께 해석하는 것이 좋습니다.", next_steps=["혈압, 혈당, 소변검사와 함께 추적을 고려하세요."], warnings=["단일 검사만으로 원인을 단정할 수 없습니다."], evidence=evidence, urgency="recheck")
    if key in {"ast","alt","ggt"} and high is not None:
        if v >= 5 * high: return build_result(key, v, li.unit, "high", f"{name}가 크게 상승했습니다.", "간세포 손상, 담도계 변화, 약물·음주·운동 등의 영향을 포함해 해석이 필요할 수 있습니다.", next_steps=["수치가 크게 상승한 경우 상담을 권합니다."], warnings=["단일 검사만으로 원인을 단정할 수 없습니다."], evidence=evidence, urgency="consult")
        if v > high: return build_result(key, v, li.unit, "borderline", f"{name}가 참고치보다 높습니다.", "경미한 상승은 일시적 변화일 수도 있어 재검이 도움이 될 수 있습니다.", next_steps=["최근 음주, 운동, 약물 여부를 확인하고 재검을 고려하세요."], warnings=["단일 검사만으로 원인을 단정할 수 없습니다."], evidence=evidence, urgency="recheck")
    short_map={"normal": f"{name}이 참고 범위 안에 있습니다.", "low": f"{name}이 낮게 측정되었습니다.", "high": f"{name}이 높게 측정되었습니다.", "unknown": f"{name}을 해석할 기준이 부족합니다."}
    urgency = "recheck" if status in {"low","high"} else "routine"
    return build_result(key, v, li.unit, status, short_map.get(status, f"{name} 결과를 확인하세요."), f"{name} 결과를 입력값과 참고치를 기준으로 해석했습니다.", next_steps=["단일 수치보다 전체 검사 맥락과 추세를 함께 보세요."], warnings=["진단을 확정하지 않습니다."], evidence=evidence, urgency=urgency)

def interpret_urine_semiquant(key, li):
    if li.value in (None, "", "미입력"): return missing_result(key)
    v=str(li.value); name=DISPLAY_NAMES_KO.get(key, key)
    explain_map={"urine_protein":"요단백은 신장과 관련된 상태를 볼 때 참고하는 정성 검사입니다.","urine_glucose":"요당은 소변에서 포도당이 검출되는지 확인하는 검사입니다.","urine_blood":"요잠혈은 소변에서 혈액 성분이 보이는지 확인하는 검사입니다.","urine_ketone":"요케톤은 지방 대사 산물이 소변에 보이는지 확인하는 검사입니다."}
    if v == "음성": return build_result(key, v, "", "normal", f"{name}이 음성입니다.", "현재 결과는 일반적으로 기대되는 범위로 보입니다.", next_steps=["다른 검사 결과와 함께 종합적으로 확인하세요."], warnings=["정성 검사 결과는 임상 맥락이 중요합니다."], evidence=[f"입력 결과: {v}"])
    if v == "trace":
        if key == "urine_protein": explain="미량의 단백이 보인 상태로, 일시적 변화일 수도 있습니다."
        elif key == "urine_glucose": explain="미량의 당이 보인 상태로, 식사나 대사 상태와 함께 해석이 필요합니다."
        elif key == "urine_blood": explain="미량의 혈액 성분이 보인 상태로, 운동이나 생리 등 일시적 영향도 고려해야 합니다."
        else: explain="미량의 케톤이 보인 상태로, 공복이나 식사 상태 영향도 있을 수 있습니다."
        return build_result(key, v, "", "borderline", f"{name}이 trace로 표시되었습니다.", explain, next_steps=["반복되면 재검을 고려하세요."], warnings=["정성 검사 결과는 임상 맥락이 중요합니다."], evidence=[f"입력 결과: {v}"], urgency="recheck")
    if v == "1+":
        steps=["반복되거나 증상이 있으면 상담을 고려하세요."]
        if key == "urine_glucose": steps=["혈당 관련 추가 확인을 고려하세요."]
        if key == "urine_blood": steps=["운동, 생리, 요로계 상태 등과 함께 해석하세요."]
        return build_result(key, v, "", "high", f"{name}이 양성(1+)으로 표시되었습니다.", explain_map.get(key, f"{name} 검사입니다."), next_steps=steps, warnings=["정성 검사 결과는 임상 맥락이 중요합니다."], evidence=[f"입력 결과: {v}"], urgency="consult")
    explain=expl  = explain_map.get(key, f"{name} 검사입니다."); steps=["지속되거나 증상이 있으면 의료진 상담이 필요할 수 있습니다."]; warnings=["정성 검사 결과는 임상 맥락이 중요합니다."]; urgency="consult"
    if key == "urine_protein": explain="단백이 비교적 뚜렷하게 검출된 상태로, 반복된다면 신장 관련 평가가 필요할 수 있습니다."; steps=["신장 관련 평가 필요 가능성이 있어 상담을 고려하세요."]
    elif key == "urine_glucose": explain="당이 비교적 뚜렷하게 검출된 상태입니다."; steps=["혈당 관련 추가 확인을 고려하세요."]
    elif key == "urine_blood": explain="혈액 성분이 비교적 뚜렷하게 보이는 상태입니다."; steps=["반복되면 요로계 평가를 고려하세요."]
    elif key == "urine_ketone": explain="케톤이 비교적 뚜렷하게 검출된 상태입니다."; warnings.append("당뇨 병력, 구토, 복통, 탈수 증상이 있으면 더 빠른 확인이 필요할 수 있습니다."); urgency="urgent" if v in {"2+","3+","4+"} else "consult"
    return build_result(key, v, "", "high", f"{name}이 양성({v})으로 표시되었습니다.", explain, next_steps=steps, warnings=warnings, evidence=[f"입력 결과: {v}"], urgency=urgency)

def build_bundle_results(person, labs, selected_keys, item_results):
    bundles=[]; result_map={r.key:r for r in item_results}
    if any(k in selected_keys for k in ["wbc","rbc","hemoglobin","hematocrit","platelet"]):
        low_rbc = result_map.get("rbc") and result_map["rbc"].status == "low"
        low_hb = result_map.get("hemoglobin") and result_map["hemoglobin"].status == "low"
        low_hct = result_map.get("hematocrit") and result_map["hematocrit"].status == "low"
        platelet_abn = result_map.get("platelet") and result_map["platelet"].status in {"borderline","high","critical","low"}
        if low_rbc and low_hb and low_hct: bundles.append(build_result("cbc_bundle","적혈구계 저하","","high","적혈구, 혈색소, 헤마토크릿이 함께 낮습니다.","적혈구 계열 전반의 저하가 보여 빈혈 가능성을 더 시사할 수 있습니다.",next_steps=["증상과 함께 CBC 추세를 보고 필요 시 상담을 고려하세요."],warnings=["CBC 종합 해석은 단일 항목보다 의미가 큽니다."],urgency="consult"))
        elif low_hb: bundles.append(build_result("cbc_bundle","혈색소 감소","","borderline","혈색소가 낮은 편입니다.","경미한 감소일 수 있으나 반복되면 추가 확인이 필요할 수 있습니다.",next_steps=["재검 또는 추가 평가를 고려하세요."],urgency="recheck"))
        elif platelet_abn: bundles.append(build_result("cbc_bundle","혈소판 변화","","borderline","혈소판 수치 변화가 있습니다.","출혈 경향 또는 반응성 변화와 함께 해석이 필요할 수 있습니다.",next_steps=["증상과 함께 수치를 추적하세요."],urgency="recheck"))
    if any(k in selected_keys for k in ["fasting_glucose","hba1c","urine_glucose"]):
        fg=result_map.get("fasting_glucose"); hba=result_map.get("hba1c"); ug=result_map.get("urine_glucose")
        if fg and hba and fg.status in {"borderline","high","critical"} and hba.status in {"borderline","high"}: bundles.append(build_result("glucose_bundle","당 대사 변화","","high","공복혈당과 당화혈색소가 함께 경계 이상입니다.","단일 검사보다 당 대사 변화 가능성을 더 시사할 수 있습니다.",next_steps=["재검 또는 추가 검사를 의료진과 상의하세요."],urgency="consult"))
        elif fg and ug and fg.status in {"high","critical"} and ug.status == "high": bundles.append(build_result("glucose_bundle","혈당 관련 확인 필요","","high","공복혈당 상승과 요당 양성이 함께 보입니다.","혈당 관련 추가 확인의 필요성을 높일 수 있습니다.",next_steps=["의료진과 상담하여 추가 평가를 고려하세요."],urgency="consult"))
    if any(k in selected_keys for k in ["creatinine","egfr","urine_protein"]):
        cr=result_map.get("creatinine"); eg=result_map.get("egfr"); up=result_map.get("urine_protein")
        if eg and up and eg.status in {"borderline","high","critical"} and up.status == "high": bundles.append(build_result("renal_bundle","신장 관련 평가 필요 가능성","","high","eGFR 저하와 요단백 양성이 함께 보입니다.","단일 결과보다 신장 관련 추가 평가 필요성을 더 시사할 수 있습니다.",next_steps=["의료진과 상의하여 추가 평가를 고려하세요."],urgency="consult"))
        elif cr and eg and cr.status == "high" and eg.status in {"borderline","high","critical"}: bundles.append(build_result("renal_bundle","신장 기능 추적 필요","","high","크레아티닌 상승과 eGFR 저하가 함께 보입니다.","신장 기능과 관련된 추적이 필요할 수 있습니다.",next_steps=["반복 검사나 상담을 고려하세요."],urgency="consult"))
    return bundles

def interpret_selected_items(person, labs, selected_keys):
    results=[]
    for key in selected_keys:
        li=labs.get(key, LabInput(unit=UNITS_DEFAULT.get(key, "")))
        if key == "bp": results.append(interpret_bp(li))
        elif key == "fasting_glucose": results.append(interpret_fasting_glucose(person, li))
        elif key == "hba1c": results.append(interpret_hba1c(person, li))
        elif key in {"urine_protein","urine_glucose","urine_blood","urine_ketone"}: results.append(interpret_urine_semiquant(key, li))
        else: results.append(interpret_generic_numeric(key, person, li))
    return results + build_bundle_results(person, labs, selected_keys, results)
