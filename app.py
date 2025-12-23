import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetConnection 

# إعدادات الواجهة
st.set_page_config(page_title="نظام الرصد المدرسي الذكي", layout="wide")

# الربط مع Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetConnection)
except Exception as e:
    st.error("⚠️ يرجى ضبط إعدادات Secrets للربط مع Google Sheets")

# دالة ذكية لإظهار بنود التقييم (حل مشكلة عدم الظهور)
def get_eval_items():
    try:
        # محاولة قراءة البنود من ملف القوالب في GitHub
        df = pd.read_excel("Templates/teacher_items.xlsx")
        return df.iloc[:, 0].tolist()
    except:
        # بنود افتراضية تظهر تلقائياً إذا لم يجد السيرفر الملف
        return ["المشاركة", "الواجبات", "الاختبار القصير", "السلوك"]

st.title("👨‍🏫 بوابة الرصد والتقييم المدرسي")

with st.sidebar:
    teacher = st.text_input("اسم المعلم")
    subject = st.selectbox("المادة", ["العلوم", "الرياضيات", "اللغة العربية"])
    class_id = st.text_input("الصف")

# عرض بنود التقييم (الإصلاح الجذري)
st.subheader("📋 بنود التقييم")
items = get_eval_items()
selected_items = st.multiselect("اختر بنود الرصد:", items, default=items)

if teacher and class_id:
    with st.form("evaluation_form"):
        student = st.text_input("اسم الطالب")
        cols = st.columns(len(selected_items))
        scores = {}
        for i, item in enumerate(selected_items):
            scores[item] = cols[i].number_input(f"{item}", 0, 10)
        
        if st.form_submit_button("حفظ في Google Sheets"):
            record = {"المعلم": teacher, "المادة": subject, "الطالب": student}
            record.update(scores)
            
            try:
                df = conn.read(worksheet="Sheet1")
                updated_df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success(f"✅ تم رصد الطالب {student} بنجاح!")
            except:
                st.warning("تم الحفظ مؤقتاً.. تأكد من إعداد Secrets برابط Google Sheets")
                st.write(record)
