import streamlit as st
import pandas as pd

# ----------------- 1. 사용자 입력 -----------------
def parse_float(input_str):
    try:
        return float(input_str)
    except:
        return 0.0  # 빈칸 또는 잘못된 입력은 0으로 처리

with st.form("target_form"):
    st.title("🎨 MATER PB 조색 계산기")
    st.markdown("타겟 색소값을 입력해 주세요. (빈칸은 0으로 처리됩니다)")

    col1, col2, col3 = st.columns(3)
    with col1:
        inno_tio2 = parse_float(st.text_input("INNO TIO2 (%)", value=""))
        ioy = parse_float(st.text_input("IOY (%)", value=""))
        xf_ioy = parse_float(st.text_input("XFINE IOY (%)", value=""))
    with col2:
        cmj = parse_float(st.text_input("CMJ (%)", value=""))
        ior = parse_float(st.text_input("IOR (%)", value=""))
        xf_ior = parse_float(st.text_input("XFINE IOR (%)", value=""))
    with col3:
        pb_usage = parse_float(st.text_input("PB 사용량 (%)", value=""))
        iob = parse_float(st.text_input("IOB (%)", value=""))
        xf_iob = parse_float(st.text_input("XFINE IOB (%)", value=""))

    submitted = st.form_submit_button("계산하기")

# ----------------- 2. 계산 실행 -----------------
if submitted:
    target = {
        "INNO_TIO2": inno_tio2,
        "CMJ": cmj,
        "IOY": ioy,
        "IOR": ior,
        "IOB": iob,
        "PB_Usage": pb_usage,
        "XFINE_IOY": xf_ioy,
        "XFINE_IOR": xf_ior,
        "XFINE_IOB": xf_iob
    }

    pb_data = [
        {"PB": 0, "PB_Percent": 18, "INNO_TIO2": 38.89, "CMJ": 44.44, "IOY": 0, "IOR": 0, "IOB": 0},
        {"PB": 1, "PB_Percent": 19, "INNO_TIO2": 36.84, "CMJ": 42.11, "IOY": 10.65, "IOR": 2.55, "IOB": 0.92},
        {"PB": 2, "PB_Percent": 20, "INNO_TIO2": 35.00, "CMJ": 30.00, "IOY": 19.89, "IOR": 2.37, "IOB": 1.72},
        {"PB": 3, "PB_Percent": 20, "INNO_TIO2": 35.00, "CMJ": 20.00, "IOY": 26.45, "IOR": 3.99, "IOB": 2.92},
        {"PB": 4, "PB_Percent": 20, "INNO_TIO2": 35.00, "CMJ": 10.00, "IOY": 27.76, "IOR": 5.00, "IOB": 3.82},
        {"PB": 5, "PB_Percent": 20, "INNO_TIO2": 35.00, "CMJ": 2.50, "IOY": 21.71, "IOR": 7.63, "IOB": 5.60},
        {"PB": 6, "PB_Percent": 22, "INNO_TIO2": 31.82, "CMJ": 0.91, "IOY": 14.29, "IOR": 8.50, "IOB": 6.40},
        {"PB": 7, "PB_Percent": 22, "INNO_TIO2": 31.82, "CMJ": 0.91, "IOY": 6.72, "IOR": 13.27, "IOB": 11.41},
        {"PB": 8, "PB_Percent": 22, "INNO_TIO2": 0.00, "CMJ": 0.00, "IOY": 21.50, "IOR": 23.00, "IOB": 29.00},
        {"PB": 9, "PB_Percent": 20, "INNO_TIO2": 0.00, "CMJ": 0.00, "IOY": 18.04, "IOR": 11.84, "IOB": 39.43},
    ]
    pb_df = pd.DataFrame(pb_data)

    # 보정계수
    CMJ_FACTOR = 0.06
    XFINE_FACTOR = {"IOY": 0.65, "IOR": 0.50, "IOB": 0.80}

    # 타겟 색소 총량 계산
    target_ioy_amt = target["IOY"] * target["PB_Usage"] / 100 + target["XFINE_IOY"] * 0.5
    target_ior_amt = target["IOR"] * target["PB_Usage"] / 100 + target["XFINE_IOR"] * 0.45
    target_iob_amt = target["IOB"] * target["PB_Usage"] / 100 + target["XFINE_IOB"] * 0.6
    target_cmj_amt = target["CMJ"] * target["PB_Usage"] / 100

    # INNO TIO2 경고
    inno_tio2_total = target["INNO_TIO2"] * target["PB_Usage"] / 100
    if inno_tio2_total < 6.99:
        st.warning(f"⚠️ 주성분 함량이 다릅니다. ({inno_tio2_total:.2f}%)")

    results = []
    for _, row in pb_df.iterrows():
        pb_cmj_amt = row["CMJ"] * row["PB_Percent"] / 100
        cmj_diff = target_cmj_amt - pb_cmj_amt
        colorant_scale = 1 + (cmj_diff * CMJ_FACTOR)

        ioy_amt = row["IOY"] * row["PB_Percent"] / 100
        ior_amt = row["IOR"] * row["PB_Percent"] / 100
        iob_amt = row["IOB"] * row["PB_Percent"] / 100

        adj_ioy_amt = ioy_amt * colorant_scale
        adj_ior_amt = ior_amt * colorant_scale
        adj_iob_amt = iob_amt * colorant_scale

        short_ioy = target_ioy_amt - adj_ioy_amt
        short_ior = target_ior_amt - adj_ior_amt
        short_iob = target_iob_amt - adj_iob_amt

        xf_ioy = short_ioy / XFINE_FACTOR["IOY"] if short_ioy > 0 else -1
        xf_ior = short_ior / XFINE_FACTOR["IOR"] if short_ior > 0 else -1
        xf_iob = short_iob / XFINE_FACTOR["IOB"] if short_iob > 0 else -1

        if xf_ioy > 0 and xf_ior > 0 and xf_iob > 0:
            total_xfine = xf_ioy + xf_ior + xf_iob
            results.append({
                "PB": row["PB"],
                "XFINE_IOY": xf_ioy,
                "XFINE_IOR": xf_ior,
                "XFINE_IOB": xf_iob,
                "TOTAL_XFINE": total_xfine
            })

    if results:
        df = pd.DataFrame(results)
        best = df.sort_values("TOTAL_XFINE").iloc[0]
        st.success(f"✅ PB 후보 2: PB {int(best['PB'])} + XFINE")
        st.markdown(f"- XFINE IOY 추가 투입량 : **{best['XFINE_IOY']:.2f}%**")
        st.markdown(f"- XFINE IOR 추가 투입량 : **{best['XFINE_IOR']:.2f}%**")
        st.markdown(f"- XFINE IOB 추가 투입량 : **{best['XFINE_IOB']:.2f}%**")
        st.markdown(f"🔷 TOTAL XFINE 투입량 : **{best['TOTAL_XFINE']:.2f}%**")
    else:
        st.error("❌ 조건을 만족하는 PB 후보가 없습니다.")
