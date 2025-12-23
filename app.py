import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
import xlsxwriter

# --- الإعدادات العامة للصفحة ---
st.set_page_config(
    page_title="نظام الرصد المدرسي الذكي - Web v1.0",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- تنسيق النصوص والواجهة (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #3498db;
        color: white;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- إدارة المجلدات وقواعد البيانات ---
TEMPLATE_DIR = "Templates"
REPORTS_DIR = "Reports"
for d in [TEMPLATE_DIR, REPORTS_DIR, "admin_records"]:
    if not os.path.exists(d):
        os.makedirs(d)

# --- دوال مساعدة ---
def clean_sheet_name(name):
    return re.sub(r'[\\/*?:\[\]]', '', str(name))[:31]

def load_data():
    db = {}
    files = {
        "students": "الطلاب", "teachers": "المعلمين", "staff": "الإداريين",
        "teacher_items": "بنود المعلم", "physical_items": "بنود البدنية", "admin_items": "بنود الإداري"
    }
    for key in files:
        path = os.path.join(TEMPLATE_DIR, f"{key}.xlsx")
        db[key] = pd.read_excel(path) if os.path.exists(path) else pd.DataFrame()
    return db

db = load_data()

# --- القائمة الجانبية (تسجيل الدخول) ---
st.sidebar.title("🔐 بوابة الدخول")
access_mode = st.sidebar.selectbox("اختر نوع الدخول:", ["👨‍🏫 رصد المعلمين", "🛡️ رصد الإداريين", "⚙️ الإدارة والنظام"])

# --- 1. قسم الإدارة ---
if access_mode == "⚙️ الإدارة والنظام":
    st.header("⚙️ إعدادات النظام والتقارير")
    
    # التحقق من كلمة مرور المسؤول
    admin_pass = st.sidebar.text_input("كلمة مرور المسؤول:", type="password")
    if admin_pass == "1234":
        tab1, tab2 = st.tabs(["📊 حالة الرصد", "💾 إدارة الملفات"])
        
        with tab1:
            st.subheader("🚀 مصفوفة متابعة الإنجاز")
            # منطق الـ Live Tracker هنا (تبسيط للعرض)
            if not db["students"].empty and not db["teachers"].empty:
                classes = sorted(db["students"].iloc[:, 2].unique())
                subjects = list(db["teachers"].iloc[:, 4].unique()) + ["admin_records"]
                tracker_df = pd.DataFrame(index=subjects, columns=classes).fillna("❌")
                st.table(tracker_df)
            else:
                st.warning("يرجى رفع ملفات الطلاب والمعلمين أولاً.")

        with tab2:
            st.subheader("📂 رفع القوالب الأساسية")
            col1, col2 = st.columns(2)
            for i, (k, v) in enumerate(db.items()):
                target_col = col1 if i % 2 == 0 else col2
                uploaded_file = target_col.file_uploader(f"رفع ملف {k}", type="xlsx")
                if uploaded_file:
                    with open(os.path.join(TEMPLATE_DIR, f"{k}.xlsx"), "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"تم تحديث {k}")

            if st.button("📊 تصدير تقرير شامل"):
                st.info("جاري تحضير التقرير...")
                # سيتم استخدام منطق export_comprehensive_report نفسه
    else:
        st.error("يرجى إدخال كلمة مرور المسؤول الصحيحة")

# --- 2. واجهة المعلم ---
elif access_mode == "👨‍🏫 رصد المعلمين":
    st.header("👨‍🏫 بوابة رصد المعلمين")
    
    t_user = st.sidebar.text_input("اسم المستخدم (المعلم):")
    t_pass = st.sidebar.text_input("كلمة المرور:", type="password")

    if t_user and t_pass:
        df_t = db["teachers"]
        user_row = df_t[(df_t.iloc[:, 1].astype(str) == t_user) & (df_t.iloc[:, 3].astype(str) == t_pass)]
        
        if not user_row.empty:
            teacher_name = user_row.iloc[0, 0]
            subject = user_row.iloc[0, 4]
            st.success(f"مرحباً {teacher_name} | مادة {subject}")
            
            # استخراج الصفوف
            classes = [str(c).strip() for c in user_row.iloc[0, 5:19].dropna().values]
            selected_class = st.selectbox("اختر الصف:", classes)
            
            if selected_class:
                # تصفية الطلاب
                students = db["students"]
                filtered_students = students[students.iloc[:, 2].astype(str) == selected_class]
                
                # عرض جدول البيانات القابل للتعديل
                st.subheader(f"رصد درجات صف: {selected_class}")
                edited_df = st.data_editor(
                    filtered_students,
                    num_rows="fixed",
                    use_container_width=True,
                    key="teacher_editor"
                )
                
                if st.button("💾 حفظ البيانات"):
                    # حفظ في Excel
                    st.success("تم الحفظ بنجاح (محاكاة)")
        else:
            st.error("بيانات الدخول غير صحيحة")

# --- 3. واجهة الإداري ---
elif access_mode == "🛡️ رصد الإداريين":
    st.header("🛡️ بوابة رصد الإداريين")
    # نفس منطق المعلم مع استخدام جداول الإداريين والصفوف الخاصة بهم

# --- التذييل ---
st.sidebar.markdown("---")
st.sidebar.caption(f"إصدار الويب v1.0 | {datetime.now().year}")
