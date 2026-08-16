import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# إعداد الصفحة
st.set_page_config(page_title="منصة ميزان AI - للجرعات الدقيقة", layout="wide", page_icon="⚖️")

# الهيدر والتعريف
st.title("⚖️ منصة ميزان | Meezan AI")
st.caption("نظام استباقي لدعم القرار الطبي وتحديد الجرعات الدقيقة بالذكاء الاصطناعي وهندسة الحركية الدوائية (PK/PD)")

# الشريط الجانبي: إعدادات المريض والمستشعرات
st.sidebar.header("📋 إعدادات الحالة والمستشعرات")

drug = st.sidebar.selectbox(
    "💊 الدواء المستهدف:",
    [
        "الوارفارين - Warfarin (مضاد تجلط)",
        "الميتفورمين - Metformin (منظم سكري)",
        "الميتوبرولول - Metoprolol (منظم نبض القلب)",
        "الثيوفيلين - Theophylline (موسع شعب هوائية)"
    ]
)

# تحديد نوع الحساس بحسب الدواء
if "Warfarin" in drug:
    sensor_name = "حساس البروتينات والتجلط الحيوي (Live CPM Sensor)"
elif "Metformin" in drug:
    sensor_name = "حساس العرق الجلدي الذكي (P2One Epidermal / MCBM Sensor)"
elif "Metoprolol" in drug:
    sensor_name = "متتبع النانو متعدد الأنماط (P2NanoTrek Wearable)"
else:
    sensor_name = "حساس المؤشرات الديناميكية والنانوية (PharmHemoSens)"

data_mode = st.sidebar.radio(
    "📡 نمط تدفق البيانات الحيوية:",
    ["إدخال مخبري يدوي (Manual)", f"بث حي من الحساس: {sensor_name}"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("👤 المعايير الفسيولوجية والحيوية")

# إدخال البيانات الأساسية
age = st.sidebar.slider("العمر (سنوات)", 18, 95, 56)
weight = st.sidebar.number_input("الوزن (كجم)", 40.0, 150.0, 78.0)
height = st.sidebar.number_input("الطول (سم)", 120.0, 210.0, 172.0)
gender = st.sidebar.radio("النوع", ["ذكر", "أنثى"], index=0)
creatinine = st.sidebar.number_input("مستوى الكرياتينين / وظائف الكلى (mg/dL)", 0.4, 5.0, 1.1)

# إدخالات خاصة بكل دواء
if "Warfarin" in drug:
    inr = st.sidebar.slider("مؤشر السيولة والتجلط (INR)", 1.0, 5.0, 2.8 if "بث حي" in data_mode else 1.8, step=0.1)
elif "Metformin" in drug:
    glucose = st.sidebar.slider("مستوى سكر الدم (mg/dL)", 70, 350, 210 if "بث حي" in data_mode else 175)
    drug_level = st.sidebar.slider("تركيز الميتفورمين في العرق (mg/L)", 0.1, 4.0, 1.4, step=0.1)
elif "Metoprolol" in drug:
    heart_rate = st.sidebar.slider("معدل ضربات القلب الحي (BPM)", 45, 140, 96 if "بث حي" in data_mode else 78)
    drug_level = st.sidebar.slider("تركيز الميتوبرولول المقاس (mg/L)", 0.05, 1.5, 0.4, step=0.05)
else: # Theophylline
    heart_rate = st.sidebar.slider("معدل ضربات القلب الحي (BPM)", 50, 150, 108 if "بث حي" in data_mode else 82)
    bp_sys = st.sidebar.slider("ضغط الدم الانقباضي (mmHg)", 90, 190, 142 if "بث حي" in data_mode else 120)
    drug_level = st.sidebar.slider("تركيز الثيوفيلين في العرق (mg/L)", 2.0, 25.0, 14.0, step=0.5)

# الحسابات الفسيولوجية
height_m = height / 100.0
bmi = weight / (height_m ** 2)
egfr = round(175 * (creatinine ** -1.154) * (age ** -0.203) * (0.742 if gender == "أنثى" else 1.0), 1)

# خوارزميات الجرعات وأنظمة الأمان
safety_warnings = []

if "Warfarin" in drug:
    base_dose = 5.0 + (0.4 if gender == "ذكر" else 0.0) - (age - 50) * 0.05 + (weight - 70) * 0.03
    if creatinine > 1.4:
        base_dose *= 0.82
        safety_warnings.append("⚠️ قصور كلوي: تم خفض الجرعة لتفادي تراكم الدواء.")
    if inr < 2.0:
        base_dose *= 1.15
        safety_warnings.append("ℹ️ مؤشر التجلط أقل من النطاق المستهدف (2.0 - 3.0)، تم رفع الجرعة لتعزيز الفعالية.")
    elif inr > 3.0:
        base_dose *= 0.75
        safety_warnings.append("🚨 خطر نزيف: مؤشر التجلط مرتفع، تم تقليل الجرعة استباقياً.")
    rec_dose = max(1.0, round(base_dose, 1))
    dose_unit = "ملجم / يومياً"

elif "Metformin" in drug:
    base_dose = 1000
    if egfr < 30:
        rec_dose = 0
        safety_warnings.append("🚨 تحذير حرج: معدل الترشيح الكلوي أقل من 30. يمنع استخدام الميتفورمين لتفادي الحماض اللبني.")
    elif egfr < 45:
        rec_dose = 500
        safety_warnings.append("⚠️ تنبيه كلوي: تم تقييد الحد الأقصى للجرعة بـ 500 ملجم.")
    else:
        if glucose > 200: base_dose = 1500
        elif glucose < 110: base_dose = 500
        if "بث حي" in data_mode and drug_level > 2.5:
            base_dose *= 0.7
            safety_warnings.append("🔬 قراءة الحساس: تركيز الدواء في العرق مرتفع، تم تعديل الجرعة استباقياً.")
        rec_dose = int(base_dose)
    dose_unit = "ملجم / مقسمة يومياً"

elif "Metoprolol" in drug:
    base_dose = 50.0
    if heart_rate < 55:
        rec_dose = 25.0
        safety_warnings.append("🚨 خطر هبوط نبض: معدل ضربات القلب منخفض جداً، تم خفض الجرعة للحد الأدنى.")
    elif heart_rate > 95:
        base_dose = 100.0
        safety_warnings.append("ℹ️ تسارع نبض: تم رفع الجرعة للوصول للتحكم المطلوب باضطراب النبض.")
        rec_dose = base_dose
    else:
        rec_dose = base_dose
    dose_unit = "ملجم / يومياً"

else: # Theophylline
    base_dose = 300.0
    if heart_rate > 105 or bp_sys > 140:
        base_dose *= 0.7
        safety_warnings.append("🚨 مؤشرات سمية مبكرة: تسارع في النبض أو ارتفاع في الضغط، تم خفض الجرعة استباقياً.")
    if "بث حي" in data_mode and drug_level > 18.0:
        base_dose *= 0.6
        safety_warnings.append("⚠️ نطاق علاجي حرج: تركيز الثيوفيلين قريب من حد السمية (>20 mg/L).")
    rec_dose = round(base_dose, 0)
    dose_unit = "ملجم / يومياً"

# عرض النتائج في الواجهة
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🎯 التوصية العلاجية الذكية")
    st.metric(label=f"الجرعة المستهدفة لدواء {drug.split()[0]}", value=f"{rec_dose} {dose_unit}")
    
    m1, m2 = st.columns(2)
    m1.metric(label="مؤشر كتلة الجسم (BMI)", value=f"{round(bmi, 1)}")
    m2.metric(label="كفاءة الكلى (eGFR)", value=f"{egfr} mL/min")
    
    st.markdown("---")
    st.subheader("🛡️ نظام الأمان وتفسير القرار الطبي")
    if "بث حي" in data_mode:
        st.info(f"📡 **اتصال مباشر:** قراءات المؤشرات الحركية والفسيولوجية مستلمة آنياً عبر `{sensor_name}`.")
    
    if safety_warnings:
        for warn in safety_warnings:
            st.warning(warn)
    else:
        st.success("✅ جميع المؤشرات الحيوية مستقرة ومتوافقة مع الجرعة القياسية المعتمدة.")
        
    st.markdown("---")
    st.subheader("📲 إشعار تطبيق المريض")
    st.info(f"🔔 **تطبيق ميزان:**\n\nاعتمد طبيبك جرعة {drug.split()[0]} بمقدار **{rec_dose} {dose_unit}**. تم تحديث الجدول العلاجي بأمان.")

with col2:
    st.subheader("📈 محاكاة الحركية الدوائية (PK Profile Simulation)")
    time = np.linspace(0, 7, 200)
    
    if "Warfarin" in drug:
        ka, ke = 1.2, (0.35 if creatinine <= 1.4 else 0.20)
        conc = (rec_dose * ka / (ka - ke)) * (np.exp(-ke * time) - np.exp(-ka * time)) * 1.6
        y_lbl, t_min, t_max = "تركيز الدواء في الدم (mg/L)", 1.5, 3.5
    elif "Metformin" in drug:
        ka, ke = 1.8, (0.50 if egfr >= 45 else 0.25)
        conc = (rec_dose / 500.0) * (ka / (ka - ke)) * (np.exp(-ke * time) - np.exp(-ka * time)) * 1.2
        y_lbl, t_min, t_max = "تركيز الدواء في الدم/العرق (mg/L)", 1.0, 2.5
    elif "Metoprolol" in drug:
        ka, ke = 1.5, 0.45
        conc = (rec_dose / 50.0) * (ka / (ka - ke)) * (np.exp(-ke * time) - np.exp(-ka * time)) * 0.8
        y_lbl, t_min, t_max = "تركيز الميتوبرولول (mg/L)", 0.2, 0.8
    else:
        ka, ke = 1.1, 0.28
        conc = (rec_dose / 300.0) * (ka / (ka - ke)) * (np.exp(-ke * time) - np.exp(-ka * time)) * 15.0
        y_lbl, t_min, t_max = "تركيز الثيوفيلين (mg/L)", 10.0, 20.0
        
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(time, conc, label="منحنى تركيز الدواء المتوقع", color="#1E3A8A", linewidth=2.5)
    ax.axhspan(t_min, t_max, color="#10B981", alpha=0.2, label="المنطقة العلاجية الآمنة (Therapeutic Window)")
    ax.axhline(t_max, color="#EF4444", linestyle="--", label="حد السمية (Toxicity Threshold)")
    ax.axhline(t_min, color="#F59E0B", linestyle="--", label="حد عدم الفعالية (Sub-Therapeutic)")
    
    ax.set_title(f"محاكاة انتشار وتراكم {drug.split()[0]} على مدار 7 أيام", fontsize=11, fontweight="bold")
    ax.set_xlabel("الزمن (أيام)", fontsize=10)
    ax.set_ylabel(y_lbl, fontsize=10)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, linestyle=":", alpha=0.6)
    st.pyplot(fig)
    
