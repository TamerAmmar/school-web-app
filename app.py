import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetConnection # مكتبة الربط بجوجل شيت

# إعدادات الصفحة
st.set_page_config(page_title="نظام الرصد المدرسي الذكي", layout="wide")

# الربط مع Google Sheets
# تأكد من وضع رابط الشيت في إعدادات Streamlit Secrets
conn = st.connection("gsheets", type=GSheetConnection)

# دالة لجلب بنود التقييم (تأكد أن الملف موجود في مجلد Templates)
def get_evaluation_items():
    try:
        # قراءة بنود التقييم من ملف اكسل محلي أو من جدول جوجل
        df_items = pd.read_excel("Templates/بنود_التقييم.xlsx")
        return df_items['البند'].tolist()
    except:
        return ["مشاركة", "واجبات", "اختبار قصير", "سلوك"] # بنود افتراضية في حال الفشل

st.title("📂 واجهة الرصد والتقييم - النسخة السحابية")

# اختيار المعلم والمادة
col1, col2 = st.columns(2)
with col1:
    teacher_name = st.text_input("اسم المعلم")
with col2:
    subject = st.selectbox("المادة", ["العلوم", "الرياضيات", "اللغة العربية"])

# عرض بنود التقييم (الإصلاح هنا)
st.subheader("✅ بنود التقييم المتاحة")
eval_items = get_evaluation_items()
selected_items = st.multiselect("اختر البنود المراد رصدها اليوم:", eval_items, default=eval_items[:2])

# شاشة الرصد
if teacher_name and selected_items:
    st.info(f"جاري الرصد للمعلم: {teacher_name} - مادة: {subject}")
    
    # نموذج إدخال البيانات
    with st.form("recording_form"):
        student_name = st.text_input("اسم الطالب")
        scores = {}
        cols = st.columns(len(selected_items))
        for i, item in enumerate(selected_items):
            scores[item] = cols[i].number_input(f"درجة {item}", min_value=0, max_value=100)
            
        submit = st.form_submit_button("حفظ البيانات في Google Sheets")
        
        if submit:
            # تجهيز البيانات للحفظ
            new_data = {"المعلم": teacher_name, "المادة": subject, "الطالب": student_name}
            new_data.update(scores)
            
            # عملية الحفظ في Google Sheets (تحديث الجدول)
            try:
                existing_data = conn.read(worksheet="Sheet1")
                updated_df = pd.concat([existing_data, pd.DataFrame([new_data])], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("✅ تم حفظ البيانات بنجاح في Google Sheets!")
            except Exception as e:
                st.error(f"خطأ في الربط: {e}")
