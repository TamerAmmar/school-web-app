import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetConnection # المكتبة التي تسبب الخطأ حالياً

# إعدادات واجهة التطبيق
st.set_page_config(page_title="نظام الرصد المدرسي الذكي", layout="wide")

# الربط مع Google Sheets
# تأكد من وضع رابط الشيت في إعدادات Streamlit Secrets كما في الشرح بالأسفل
try:
    conn = st.connection("gsheets", type=GSheetConnection)
except Exception:
    st.error("خطأ: يرجى إعداد Secrets في لوحة تحكم Streamlit للربط مع Google Sheets")

# دالة ذكية لجلب بنود التقييم لضمان ظهورها دائماً
def load_evaluation_items():
    try:
        # محاولة التحميل من ملف محلي إذا كان مرفوعاً على GitHub
        items_df = pd.read_excel("Templates/teacher_items.xlsx")
        return items_df.iloc[:, 0].tolist()
    except Exception:
        # بنود افتراضية تظهر تلقائياً في حال فقدان الملف لضمان عمل شاشة الرصد
        return ["المشاركة الصفية", "الالتزام بالواجبات", "الاختبار القصير", "السلوك العام"]

st.title("👨‍🏫 بوابة الرصد والتقييم المدرسي الذكية")

# القائمة الجانبية لإدخال البيانات الأساسية
with st.sidebar:
    st.header("📋 بيانات الحصة")
    teacher_name = st.text_input("اسم المعلم")
    subject = st.selectbox("المادة", ["العلوم", "الرياضيات", "اللغة العربية", "التقنية الرقمية"])
    class_name = st.text_input("الصف الدراسي (مثلاً: 7/أ)")

# إصلاح مشكلة بنود التقييم: استدعاء وعرض البنود
st.subheader("✅ بنود التقييم المتاحة")
available_items = load_evaluation_items()
selected_items = st.multiselect("حدد البنود التي تود رصدها الآن:", available_items, default=available_items)

# نموذج الرصد وإرسال البيانات
if teacher_name and class_name:
    st.info(f"جاري الرصد للصف: {class_name}")
    
    with st.form("recording_form"):
        student_name = st.text_input("اسم الطالب")
        
        # توزيع البنود المختارة في أعمدة ديناميكية
        cols = st.columns(len(selected_items))
        scores = {}
        for idx, item in enumerate(selected_items):
            scores[item] = cols[idx].number_input(f"{item}", min_value=0, max_value=10, step=1)
            
        submit_btn = st.form_submit_button("حفظ الرصد في Google Sheets")
        
        if submit_btn:
            # تجهيز السجل للحفظ
            record = {
                "التاريخ": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                "المعلم": teacher_name,
                "المادة": subject,
                "الصف": class_name,
                "الطالب": student_name
            }
            record.update(scores)
            
            try:
                # عملية الحفظ السحابي
                existing_data = conn.read(worksheet="Sheet1")
                updated_df = pd.concat([existing_data, pd.DataFrame([record])], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success(f"✅ تم حفظ درجات الطالب {student_name} بنجاح!")
            except Exception as e:
                st.error(f"فشل الربط مع Google Sheets. تفاصيل: {e}")
                # عرض البيانات في حال فشل الربط لتسهيل نسخها يدوياً
                st.write("البيانات التي لم يتم حفظها:", record)
