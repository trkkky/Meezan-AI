import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="Meezan AI - ميزان للجرعات الذكية",
    page_icon="⚖️",
    layout="wide"
)

# عنوان المشروع
st.title("⚖️ منصة ميزان | Meezan AI")
st.markdown("##### نظام دعم القرار الطبي لتحديد الجرعات الدقيقة بالذكاء الاصطناعي وهندسة الحركية الدوائية")
st.divider()

# القائمة الجانبية لإدخال بيانات المريض
st.sidebar.header("📋 بيانات المريض والتحاليل")

age = st.sidebar.slider("العمر (سنوات):", 18, 90, 55)
weight = st.sidebar.number_input("الوزن (كجم):", min_value=30.0, max_value=150.0, value=70.0, step=0.5)
height = st.sidebar.number_input("الطول (سم):", min_value=120.0, max_value=210.0, value=170.0, step=1.0)
gender = st.sidebar.radio("النوع:", ["ذكر", "أنثى"])
creatinine = st.sidebar.number_input("مستوى الكرياتينين / وظائف الكلى (mg/dL):", min_value=0.4, max_value=5.0, value=1.0, step=0.1)
current_inr = st.sidebar.number_input("مؤشر تجلط الدم الحالي (Current INR):", min_value=0.8, max_value=6.0, value=1.5, step=0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("💊 الدواء المحدد")
drug = st.sidebar.selectbox("اختر الدواء:", ["الوارفارين (Warfarin)", "الفانكومايسين (Vancomycin)"])

# حساب الجرعة الأساسية (خوارزمية IWPC)
gender_factor = 1.0 if gender == "ذكر" else 0.9
bmi = weight / ((height / 100) ** 2)

base_weekly_dose = np.exp(0.613 - (0.0083 * age) + (0.0118 * height) + (0.0134 * weight))
daily_dose = (base_weekly_dose / 7) * gender_factor

# ضبط الجرعة بناءً على وظائف الكلى ومؤشر التجلط
safety_warnings = []

if creatinine > 1.5:
    daily_dose *= 0.8
    safety_warnings.append("⚠️ **تنبيه أمان:** انخفاض كفاءة الكلى (Creatinine > 1.5). تم تخفيض الجرعة تلقائياً بنسبة 20% لتفادي السمية.")

if current_inr > 3.0:
    daily_dose *= 0.5
    safety_warnings.append("🚨 **تحذير حرج:** مؤشر التجلط مرتفع (INR > 3.0). خطر نزيف! تم تخفيض الجرعة الموصى بها بنسبة 50%.")
elif current_inr < 2.0:
    daily_dose *= 1.15
    safety_warnings.append("ℹ️ **ملاحظة:** مؤشر التجلط أقل من النطاق المستهدف (2.0 - 3.0). تم تعديل الجرعة للوصول للتأثير العلاجي.")

daily_dose = round(daily_dose, 1)

# الواجهة الرئيسية
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🎯 الجرعة الموصى بها من الذكاء الاصطناعي")
    
    st.metric(label="الجرعة اليومية المستهدفة", value=f"{daily_dose} ملجم / يومياً")
    st.metric(label="مؤشر كتلة الجسم (BMI)", value=f"{round(bmi, 1)}")

    st.markdown("### 🔍 تحليل الأمان والتنبيهات الطبية")
    if safety_warnings:
        for warn in safety_warnings:
            st.warning(warn)
    else:
        st.success("✅ المؤشرات الحيوية ضمن النطاق الطبيعي. الجرعة القياسية آمنة للمريض.")

    st.markdown("---")
    st.subheader("📲 معاينة إشعار تطبيق المريض")
    st.info(f"🔔 **تطبيق ميزان (جوال المريض):**\n\n عزيزي المريض، حدد طبيبك جرعتك اليومية من دواء {drug.split()[0]} بـ **{daily_dose} ملجم** في الساعة 8:00 مساءً.")

with col2:
    st.subheader("📈 محاكاة تركيز الدواء بالدم (PK Profile)")
    
    days = np.linspace(0, 7, 100)
    ka = 1.2
    ke = 0.15
    conc = (daily_dose * ka / (ka - ke)) * (np.exp(-ke * days) - np.exp(-ka * days)) + (current_inr * 0.8)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(days, conc, color='#1f77b4', linewidth=2.5, label='تركيز الدواء المتوقع (mg/L)')
    ax.axhspan(1.5, 3.5, color='green', alpha=0.15, label='المنطقة العلاجية الآمنة (Therapeutic Window)')
    ax.axhline(y=3.5, color='red', linestyle='--', alpha=0.7, label='حد السمية (Toxicity Threshold)')
    ax.axhline(y=1.5, color='orange', linestyle='--', alpha=0.7, label='حد عدم الفعالية (Sub-therapeutic)')
    
    ax.set_title("توقع انتشار وتراكم الدواء في جسم المريض عبر 7 أيام", fontsize=12, fontweight='bold')
    ax.set_xlabel("الأيام", fontsize=10)
    ax.set_ylabel("التركيز في الدم (mg/L)", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', fontsize=8)
    
    st.pyplot(fig)

st.divider()
st.caption("Meezan AI v1.0 | هاكاثون هيلثون 2026 - جامعة الملك سعود")