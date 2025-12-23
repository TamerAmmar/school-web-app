import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetConnection 

# إعدادات واجهة التطبيق
st.set_page_config(page_title="نظام الرصد المدرسي الذكي", layout="wide")

# محاولة الربط السحابي مع Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetConnection)
except Exception:
    st.warning("يُرجى إكمال إعداد Secrets في لوحة تحكم Streamlit للربط مع Google Sheets.")

# وظيفة برمجية لضمان ظهور بنود التقييم دائماً
def load_evaluation_items():
    try:
        # محاولة التحميل من ملف قوالب المعلم إذا وجد في GitHub
        items_df = pd.read_excel("Templates/teacher_items.xlsx")
        return items_df.iloc[:, 0].tolist()
    except Exception:
        # بنود افتراضية تظهر تلقائياً في حال فقدان الملف (حل مشكلة عدم الظهور)
        return ["المشاركة الصفية", "الالتزام بالواجبات", "الاختبار القصير", "السلوك العام"]

st.title("👨‍🏫 بوابة الرصد والتقييم المدرسي")

# القائمة الجانبية للبيانات
with st.sidebar:
    st.header("إعدادات الحصة")
    teacher_name = st.text_input("اسم المعلم")
    subject = st.selectbox("المادة", ["العلوم", "الرياضيات", "اللغة العربية", "التقنية الرقمية"])
    class_id = st.text_input("الصف الدراسي")

# قسم بنود التقييم (الإصلاح الجذري)
st.subheader("📋 بنود التقييم المتاحة")
available_items = load_evaluation_items()
selected_items = st.multiselect("اختر البنود التي تريد رصدها الآن:", available_items, default=available_items)

# نموذج إدخال الدرجات
if teacher_name and class_id:
    with st.form("recording_form"):
        student_name = st.text_input("اسم الطالب")
        
        # توزيع البنود المختارة في أعمدة متساوية
        cols = st.columns(len(selected_items))
        student_grades = {}
        for idx, item in enumerate(selected_items):
            student_grades[item] = cols[idx].number_input(f"{item}", min_value=0, max_value=10, step=1)
        
        save_btn = st.form_submit_button("حفظ الرصد سحابياً")
        
        if save_btn:
            # تجهيز البيانات بصيغة جدولية
            record = {
                "التاريخ": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                "المعلم": teacher_name,
                "المادة": subject,
                "الصف": class_id,
                "الطالب": student_name
            }
            record.update(student_grades)
            
            try:
                # عملية التحديث السحابي في Google Sheets
                existing_df = conn.read(worksheet="Sheet1")
                updated_df = pd.concat([existing_df, pd.DataFrame([record])], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success(f"✅ تم حفظ درجات الطالب {student_name} في السحابة بنجاح!")
            except Exception:
                st.error("فشل الحفظ السحابي. يرجى التأكد من صلاحيات رابط Google Sheets.")
