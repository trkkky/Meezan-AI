import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# إعداد الصفحة
st.set_page_config(page_title="منصة ميزان AI - للجرعات الدقيقة", layout="wide", page_icon="⚖️")

# عنوان المنصة
st.title("⚖️ منصة ميزان | Meezan AI")
st.caption("نظام استباقي لتحديد الجرعات الدقيقة بالذكاء الاصطناعي وهندسة الحركية الدوائية (PK/PD) ورقع الاستشعار النانوية")

# الشريط الجانبي: إدخال البيانات ومصدر القياس
st.sidebar.header("📋 إعدادات المريض والمستشعرات")

drug = st.sidebar.selectbox("💊 الدواء المستهدف", ["الوارفارين (Warfarin)", "الميتفورمين (Metformin)"])

if drug == "الميتفورمين (Metformin)":
    data_source = st.sidebar.radio(
        "📡 مصدر تدفق البيانات الحيوية:",
        ["إدخال مخبري يدوي (Manual)", "رقعة الإبر المجهرية النانوية الذكية (Wearable MCBM Patch)"]
    )
else:
    data_source = st.sidebar.radio(
        "📡 مصدر تدفق البيانات الحيوية:",
        ["إدخال مخبري يدوي (Manual)", "حساس المراقبة المستمرة المباشر (Live CPM Sensor)"]
    )

st.sidebar.markdown("---")
st.sidebar.subheader("👤 المؤشرات الحيوية والفسيولوجية")

if "MCBM" in data_source:
    st.sidebar.success("🟢 رقعة MCBM متصلة: بث حي لتركيز الدواء وسكر الدم من السائل الخلالي (ISF)")
    age = st.sidebar.slider("العمر (سنوات)", 18, 100, 52)
    weight = st.sidebar.number_input("الوزن (كجم)", 40.0, 150.0, 85.0)
    height = st.sidebar.number_input("الطول (سم)", 120.0, 210.0, 175.0)
    gender = st.sidebar.radio("النوع", ["ذكر", "أنثى"], index=0)
    creatinine = st.sidebar.number_input("مستوى الكرياتينين / وظائف الكلى (mg/dL)", 0.4, 6.0, 1.1)
    glucose = st.sidebar.slider("مستوى سكر الدم الحي من الرقعة (mg/dL)", 70, 350, 195)
    drug_level = st.sidebar.slider("تركيز الدواء المقاس من الرقعة النانوية (mg/L)", 0.1, 4.0, 1.2, step=0.1)
elif "CPM" in data_source:
    st.sidebar.success("🟢 متصل بحساس CPM: بث حي للمؤشرات الحيوية والتجلط")
    age = st.sidebar.slider("العمر (سنوات)", 18, 100, 58)
    weight = st.sidebar.number_input("الوزن (كجم)", 40.0, 150.0, 74.0)
    height = st.sidebar.number_input("الطول (سم)", 120.0, 210.0, 172.0)
    gender = st.sidebar.radio("النوع", ["ذكر", "أنثى"], index=0)
    creatinine = st.sidebar.number_input("مستوى الكرياتينين / وظائف الكلى (mg/dL)", 0.4, 6.0, 1.3)
    inr = st.sidebar.slider("مؤشر السيولة الحي من الحساس (Live CPM - INR)", 1.0, 5.0, 2.8, step=0.1)
else:
    age = st.sidebar.slider("العمر (سنوات)", 18, 100, 60)
    weight = st.sidebar.number_input("الوزن (كجم)", 40.0, 150.0, 75.0)
    height = st.sidebar.number_input("الطول (سم)", 120.0, 210.0, 170.0)
    gender = st.sidebar.radio("النوع", ["ذكر", "أنثى"], index=0)
    creatinine = st.sidebar.number_input("مستوى الكرياتينين / وظائف الكلى (mg/dL)", 0.4, 6.0, 1.2)
    if drug == "الوارفارين (Warfarin)":
        inr = st.sidebar.number_input("مؤشر تجلط الدم الحالي (Current INR)", 1.0, 5.0, 1.8)
    else:
        glucose = st.sidebar.number_input("مستوى السكر التراكمي/الصائم (mg/dL)", 70, 350, 180)

# الحسابات الفسيولوجية
height_m = height / 100.0
bmi = weight / (height_m ** 2)
egfr = round(175 * (creatinine ** -1.154) * (age ** -0.203) * (0.742 if gender == "أنثى" else 1.0), 1)

safety_warnings = []

# خوارزمية الجرعات
if drug == "الوارفارين (Warfarin)":
    base_dose = 5.0
    if gender == "ذكر":
        base_dose += 0.4
    base_dose -= (age - 50) * 0.05
    base_dose += (weight - 70) * 0.03
    
    if creatinine > 1.4:
        base_dose *= 0.82
        safety_warnings.append("⚠️ تنبيه كلوي: تم خفض الجرعة تلقائياً لوجود قصور في وظائف الكلى.")
        
    if inr < 2.0:
        base_dose *= 1.15
        safety_warnings.append("ℹ️ مؤشر التجلط أقل من النطاق المستهدف (2.0 - 3.0)، تم رفع الجرعة لتعزيز الفعالية.")
    elif inr > 3.0:
        base_dose *= 0.75
        safety_warnings.append("🚨 خطر نزيف: مؤشر التجلط مرتفع، تم تقليل الجرعة استباقياً لتفادي النزيف.")
        
    recommended_dose = max(1.0, round(base_dose, 1))
    dose_unit = "ملجم / يومياً"

else: # Metformin
    base_dose = 1000
    if egfr < 30:
        recommended_dose = 0
        safety_warnings.append("🚨 تحذير حرج: معدل الترشيح الكلوي (eGFR < 30). يمنع استخدام الميتفورمين لتفادي الحماض اللبني (Lactic Acidosis).")
    elif egfr < 45:
        base_dose = 500
        safety_warnings.append("⚠️ تنبيه كلوي: تم تقييد الحد الأقصى للجرعة بـ 500 ملجم بسبب انخفاض كفاءة الكلى.")
    else:
        if glucose > 200:
            base_dose = 1500
            safety_warnings.append("ℹ️ استجابة السكر: ارتفاع سكر الدم استدعى رفع الجرعة للتحكم الأيضي الأمثل.")
        elif glucose < 110:
            base_dose = 500
            safety_warnings.append("ℹ️ استقرار السكر: مستوى سكر الدم منضبط، تم اعتماد الجرعة الدنيا الوقائية.")
            
    if "MCBM" in data_source and drug_level > 2.5:
        base_dose *= 0.7
        safety_warnings.append("🔬 قراءة رقعة MCBM: تركيز الميتفورمين في السائل الخلالي مرتفع، تم تعديل الجرعة استباقياً لتفادي السمية.")
        
    recommended_dose = int(base_dose)
    dose_unit = "ملجم / مقسمة يومياً"

# عرض النتائج
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🎯 التوصية العلاجية الذكية")
    st.metric(label=f"الجرعة المقترحة لدواء {drug.split()[0]}", value=f"{recommended_dose} {dose_unit}")
    
    m_col1, m_col2 = st.columns(2)
    m_col1.metric(label="مؤشر كتلة الجسم (BMI)", value=f"{round(bmi, 1)}")
    m_col2.metric(label="معدل كفاءة الكلى (eGFR)", value=f"{egfr} mL/min")
    
    st.markdown("---")
    st.subheader("🛡️ نظام الأمان وتفسير القرار الطبي")
    
    if "MCBM" in data_source:
        st.info("🧬 **تقنية MCBM النانوية:** البيانات مستلمة عبر رقعة الإبر المجهرية بالتحليل الكهروكيميائي للإنزيمات النانوية (Layer-by-Layer Nanoenzymes).")
    elif "CPM" in data_source:
        st.info("📡 **حساس CPM:** اتصال مستمر لنظام الحركية الدوائية المغلق (Closed-Loop PK System).")
        
    if safety_warnings:
        for warn in safety_warnings:
            st.warning(warn)
    else:
        st.success("✅ جميع المؤشرات الحيوية مستقرة ومتوافقة مع الجرعة القياسية.")
        
    st.markdown("---")
    st.subheader("📲 إشعار تطبيق المريض")
    st.info(f"🔔 **تطبيق ميزان:**\n\nاعتمد طبيبك جرعة {drug.split()[0]} بمقدار **{recommended_dose} {dose_unit}**. تم تحديث جدول الأدوية تلقائياً.")

with col2:
    st.subheader("📈 محاكاة الحركية الدوائية (PK Profile Simulation)")
    
    time = np.linspace(0, 7, 200)
    
    if drug == "الوارفارين (Warfarin)":
        ka = 1.2
        ke = 0.35 if creatinine <= 1.4 else 0.20
        conc = (recommended_dose * ka / (ka - ke)) * (np.exp(-ke * time) - np.exp(-ka * time)) * 1.6
        y_label = "تركيز الدواء في الدم (mg/L)"
        target_min, target_max = 1.5, 3.5
    else:
        ka = 1.8
        ke = 0.50 if egfr >= 45 else 0.25
        conc = (recommended_dose / 500.0) * (ka / (ka - ke)) * (np.exp(-ke * time) - np.exp(-ka * time)) * 1.2
        y_label = "تركيز الميتفورمين في السائل الخلالي ISF (mg/L)"
        target_min, target_max = 1.0, 2.5
        
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(time, conc, label="منحنى تركيز الدواء المتوقع", color="#1E3A8A", linewidth=2.5)
    
    ax.axhspan(target_min, target_max, color="#10B981", alpha=0.2, label="المنطقة العلاجية الآمنة (Therapeutic Window)")
    ax.axhline(target_max, color="#EF4444", linestyle="--", label="حد السمية (Toxicity Threshold)")
    ax.axhline(target_min, color="#F59E0B", linestyle="--", label="حد عدم الفعالية (Sub-Therapeutic)")
    
    ax.set_title(f"محاكاة انتشار وتراكم {drug.split()[0]} على مدار 7 أيام", fontsize=11, fontweight="bold")
    ax.set_xlabel("الزمن (أيام)", fontsize=10)
    ax.set_ylabel(y_label, fontsize=10)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, linestyle=":", alpha=0.6)
    
    st.pyplot(fig)
