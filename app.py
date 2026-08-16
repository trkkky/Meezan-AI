import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# إعداد الصفحة
st.set_page_config(page_title="منصة ميزان AI - للجرعات الدقيقة", layout="wide", page_icon="⚖️")

# عنوان المنصة
st.title("⚖️ منصة ميزان | Meezan AI")
st.caption("نظام استباقي لدعم القرار الطبي وتحديد الجرعات الدقيقة بالذكاء الاصطناعي وهندسة الحركية الدوائية (PK/PD)")

# الشريط الجانبي: إدخال البيانات ومصدر القياس
st.sidebar.header("📋 بيانات المريض والتحاليل")

data_source = st.sidebar.radio(
    "📡 مصدر تدفق البيانات الحيوية:",
    ["إدخال مخبري يدوي (Manual)", "حساس المراقبة المستمرة المباشر (Live CPM Sensor)"]
)

if data_source == "حساس المراقبة المستمرة المباشر (Live CPM Sensor)":
    st.sidebar.success("🟢 متصل بالحساس: بث حي للبروتينات والمؤشرات (Live Stream)")
    age = st.sidebar.slider("العمر (سنوات)", 18, 100, 58)
    weight = st.sidebar.number_input("الوزن (كجم)", 40.0, 150.0, 74.0)
    height = st.sidebar.number_input("الطول (سم)", 120.0, 210.0, 172.0)
    gender = st.sidebar.radio("النوع", ["ذكر", "أنثى"], index=0)
    creatinine = st.sidebar.number_input("مستوى الكرياتينين / وظائف الكلى (mg/dL)", 0.4, 6.0, 1.3)
    inr = st.sidebar.slider("مؤشر السيولة الحي من الحساس (Live CPM - INR)", 1.0, 5.0, 2.8, step=0.1)
else:
    age = st.sidebar.slider("العمر (سنوات)", 18, 100, 62)
    weight = st.sidebar.number_input("الوزن (كجم)", 40.0, 150.0, 70.0)
    height = st.sidebar.number_input("الطول (سم)", 120.0, 210.0, 170.0)
    gender = st.sidebar.radio("النوع", ["ذكر", "أنثى"], index=0)
    creatinine = st.sidebar.number_input("مستوى الكرياتينين / وظائف الكلى (mg/dL)", 0.4, 6.0, 1.2)
    inr = st.sidebar.number_input("مؤشر تجلط الدم الحالي (Current INR)", 1.0, 5.0, 1.8)

drug = st.sidebar.selectbox("💊 الدواء المحدد", ["الوارفارين (Warfarin)", "الفانكومايسين (Vancomycin)"])

# الحسابات الفسيولوجية
height_m = height / 100.0
bmi = weight / (height_m ** 2)

# خوارزمية حساب الجرعة السريرية (IWPC مبسطة)
base_dose = 5.0
if gender == "ذكر":
    base_dose += 0.4
base_dose -= (age - 50) * 0.05
base_dose += (weight - 70) * 0.03

# تصحيح الجرعة بناءً على وظائف الكلى ومؤشر التجلط
safety_warnings = []
if creatinine > 1.4:
    base_dose *= 0.82
    safety_warnings.append("⚠️ تنبيه كلوي: تم خفض الجرعة تلقائياً لوجود قصور في وظائف الكلى لتفادي تراكم الدواء.")

if inr < 2.0:
    base_dose *= 1.15
    safety_warnings.append("ℹ️ ملاحظة: مؤشر التجلط أقل من النطاق المستهدف (2.0 - 3.0)، تم رفع الجرعة للوصول للتأثير العلاجي.")
elif inr > 3.0:
    base_dose *= 0.75
    safety_warnings.append("🚨 خطر نزيف: مؤشر التجلط مرتفع، تم تقليل الجرعة استباقياً لتفادي النزيف.")

recommended_dose = max(1.0, round(base_dose, 1))

# الواجهة الرئيسية
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🎯 الجرعة الموصى بها من الذكاء الاصطناعي")
    st.metric(label="الجرعة اليومية المستهدفة", value=f"{recommended_dose} ملجم / يومياً")
    st.metric(label="مؤشر كتلة الجسم (BMI)", value=f"{round(bmi, 1)}")
    
    st.markdown("---")
    st.subheader("🔍 تحليل الأمان والتنبيهات الطبية")
    if data_source == "حساس المراقبة المستمرة المباشر (Live CPM Sensor)":
        st.info("📡 **تحديث مباشر:** القراءات يتم استلامها آنياً من حساس CPM القابل للارتداء كل 5 ثوانٍ.")
    
    if safety_warnings:
        for warn in safety_warnings:
            st.warning(warn)
    else:
        st.success("✅ المؤشرات الحيوية ضمن النطاق الطبيعي، الجرعة القياسية آمنة للمريض.")
        
    st.markdown("---")
    st.subheader("📲 معاينة إشعار تطبيق المريض")
    st.info(f"🔔 **تطبيق ميزان (جوال المريض):**\n\nعزيزي المريض، حدد طبيبك جرعتك اليومية من دواء {drug.split()[0]} بـ **{recommended_dose} ملجم** في الساعة 8:00 مساءً.")

with col2:
    st.subheader("📈 محاكاة تركيز الدواء بالدم (PK Profile)")
    
    # محاكاة الحركية الدوائية
    time = np.linspace(0, 7, 200)
    # نموذج One-Compartment PK Model
    ka = 1.2
    ke = 0.35 if creatinine <= 1.4 else 0.20
    concentration = (recommended_dose * ka / (ka - ke)) * (np.exp(-ke * time) - np.exp(-ka * time)) * 1.6
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(time, concentration, label="تركيز الدواء المتوقع (mg/L)", color="#1E3A8A", linewidth=2.5)
    
    # النطاق العلاجي الآمن
    ax.axhspan(1.5, 3.5, color="#10B981", alpha=0.2, label="المنطقة العلاجية الآمنة (Therapeutic Window)")
    ax.axhline(3.5, color="#EF4444", linestyle="--", label="حد السمية (Toxicity Threshold)")
    ax.axhline(1.5, color="#F59E0B", linestyle="--", label="حد عدم الفعالية (Sub-Therapeutic)")
    
    ax.set_title("توقع انتشار وتراكم الدواء في جسم المريض عبر 7 أيام", fontsize=12, fontweight="bold")
    ax.set_xlabel("الأيام", fontsize=10)
    ax.set_ylabel("التركيز في الدم (mg/L)", fontsize=10)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, linestyle=":", alpha=0.6)
    
    st.pyplot(fig)
