TEST_CATEGORIES = {
    "건강검진 기본검사": [
        "fasting_glucose", "hba1c", "total_chol", "ldl", "hdl", "tg",
        "ast", "alt", "ggt", "creatinine", "egfr", "uric_acid", "bp"
    ],
    "CBC 혈액검사": ["wbc", "rbc", "hemoglobin", "hematocrit", "platelet"],
    "소변검사": ["urine_protein", "urine_glucose", "urine_blood", "urine_ketone", "urine_ph", "urine_specific_gravity"]
}

TEST_GROUPS = {
    "건강검진 기본검사": {
        "당 대사": ["fasting_glucose", "hba1c"],
        "지질 검사": ["total_chol", "ldl", "hdl", "tg"],
        "간 기능": ["ast", "alt", "ggt"],
        "신장/요산": ["creatinine", "egfr", "uric_acid"],
        "혈압": ["bp"]
    },
    "CBC 혈액검사": {
        "백혈구": ["wbc"],
        "적혈구계": ["rbc", "hemoglobin", "hematocrit"],
        "혈소판": ["platelet"]
    },
    "소변검사": {
        "정성 검사": ["urine_protein", "urine_glucose", "urine_blood", "urine_ketone"],
        "수치 검사": ["urine_ph", "urine_specific_gravity"]
    }
}

DISPLAY_NAMES_KO = {
    "fasting_glucose": "공복혈당", "hba1c": "당화혈색소(HbA1c)", "total_chol": "총콜레스테롤", "ldl": "LDL 콜레스테롤",
    "hdl": "HDL 콜레스테롤", "tg": "중성지방(TG)", "ast": "AST(GOT)", "alt": "ALT(GPT)", "ggt": "감마지티피(GGT)",
    "creatinine": "크레아티닌", "egfr": "eGFR(추정사구체여과율)", "uric_acid": "요산", "bp": "혈압",
    "wbc": "백혈구(WBC)", "rbc": "적혈구(RBC)", "hemoglobin": "혈색소(Hb)", "hematocrit": "헤마토크릿(Hct)", "platelet": "혈소판(Platelet)",
    "urine_protein": "요단백", "urine_glucose": "요당", "urine_blood": "요잠혈", "urine_ketone": "요케톤", "urine_ph": "소변 pH", "urine_specific_gravity": "요비중",
    "cbc_bundle": "CBC 종합 해석", "glucose_bundle": "당 대사 종합 해석", "renal_bundle": "신장/소변 종합 해석"
}

UNITS_DEFAULT = {
    "fasting_glucose": "mg/dL", "hba1c": "%", "total_chol": "mg/dL", "ldl": "mg/dL", "hdl": "mg/dL", "tg": "mg/dL",
    "ast": "U/L", "alt": "U/L", "ggt": "U/L", "creatinine": "mg/dL", "egfr": "mL/min/1.73m²", "uric_acid": "mg/dL",
    "bp": "mmHg", "wbc": "x10³/µL", "rbc": "x10⁶/µL", "hemoglobin": "g/dL", "hematocrit": "%", "platelet": "x10³/µL",
    "urine_protein": "", "urine_glucose": "", "urine_blood": "", "urine_ketone": "", "urine_ph": "", "urine_specific_gravity": ""
}

LAB_META = {
    "fasting_glucose": {"input_type": "numeric", "default_ref": {"low": 70, "high": 99}, "min": 0.0, "max": 600.0, "step": 1.0},
    "hba1c": {"input_type": "numeric", "default_ref": {"low": None, "high": 5.6}, "min": 0.0, "max": 20.0, "step": 0.1},
    "total_chol": {"input_type": "numeric", "default_ref": {"low": None, "high": 199}, "min": 0.0, "max": 600.0, "step": 1.0},
    "ldl": {"input_type": "numeric", "default_ref": {"low": None, "high": 129}, "min": 0.0, "max": 500.0, "step": 1.0},
    "hdl": {"input_type": "numeric", "default_ref_male": {"low": 40, "high": None}, "default_ref_female": {"low": 40, "high": None}, "min": 0.0, "max": 150.0, "step": 1.0},
    "tg": {"input_type": "numeric", "default_ref": {"low": None, "high": 149}, "min": 0.0, "max": 2000.0, "step": 1.0},
    "ast": {"input_type": "numeric", "default_ref": {"low": None, "high": 32}, "min": 0.0, "max": 3000.0, "step": 1.0},
    "alt": {"input_type": "numeric", "default_ref": {"low": None, "high": 32}, "min": 0.0, "max": 3000.0, "step": 1.0},
    "ggt": {"input_type": "numeric", "default_ref_male": {"low": 11, "high": 63}, "default_ref_female": {"low": 8, "high": 35}, "min": 0.0, "max": 3000.0, "step": 1.0},
    "creatinine": {"input_type": "numeric", "default_ref_male": {"low": 0.7, "high": 1.3}, "default_ref_female": {"low": 0.6, "high": 1.1}, "min": 0.0, "max": 20.0, "step": 0.01},
    "egfr": {"input_type": "numeric", "default_ref": {"low": 90, "high": None}, "min": 0.0, "max": 200.0, "step": 1.0},
    "uric_acid": {"input_type": "numeric", "default_ref_male": {"low": 3.4, "high": 7.0}, "default_ref_female": {"low": 2.4, "high": 6.0}, "min": 0.0, "max": 20.0, "step": 0.1},
    "bp": {"input_type": "bp_text", "placeholder": "예: 120/80"},
    "wbc": {"input_type": "numeric", "default_ref": {"low": 4.0, "high": 10.0}, "min": 0.0, "max": 100.0, "step": 0.1},
    "rbc": {"input_type": "numeric", "default_ref_male": {"low": 4.5, "high": 5.9}, "default_ref_female": {"low": 4.0, "high": 5.2}, "min": 0.0, "max": 10.0, "step": 0.01},
    "hemoglobin": {"input_type": "numeric", "default_ref_male": {"low": 13.0, "high": 16.0}, "default_ref_female": {"low": 12.0, "high": 15.0}, "min": 0.0, "max": 25.0, "step": 0.1},
    "hematocrit": {"input_type": "numeric", "default_ref_male": {"low": 39.0, "high": 52.0}, "default_ref_female": {"low": 36.0, "high": 48.0}, "min": 0.0, "max": 80.0, "step": 0.1},
    "platelet": {"input_type": "numeric", "default_ref": {"low": 300, "high": 500}, "min": 0.0, "max": 2000.0, "step": 1.0},
    "urine_protein": {"input_type": "categorical", "choices": ["미입력", "음성", "trace", "1+", "2+", "3+", "4+"]},
    "urine_glucose": {"input_type": "categorical", "choices": ["미입력", "음성", "trace", "1+", "2+", "3+", "4+"]},
    "urine_blood": {"input_type": "categorical", "choices": ["미입력", "음성", "trace", "1+", "2+", "3+", "4+"]},
    "urine_ketone": {"input_type": "categorical", "choices": ["미입력", "음성", "trace", "1+", "2+", "3+", "4+"]},
    "urine_ph": {"input_type": "numeric", "default_ref": {"low": 5.0, "high": 8.0}, "min": 3.0, "max": 10.0, "step": 0.1},
    "urine_specific_gravity": {"input_type": "numeric", "default_ref": {"low": 1.005, "high": 1.030}, "min": 1.0, "max": 1.1, "step": 0.001}
}
