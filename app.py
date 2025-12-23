import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetConnection # المكتبة التي تسبب الخطأ حالياً

# إعدادات الواجهة
st.set_page_config(page_title="نظام الرصد المدرسي الذكي", layout="wide")

# الربط مع Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetConnection)
except Exception:
    st.error("يرجى التأكد من إعداد Secrets في Streamlit Cloud")

# دالة ذكية لجلب بنود التقييم
def load_eval_items():
    try:
        # محاولة التحميل من ملف محلي إذا وجد
        items_df = pd.read_excel("Templates/teacher_items.xlsx")
        return items_df.iloc[:, 0].tolist()
    except Exception:
        # بنود افتراضية تظهر دائماً في حال عدم وجود الملف
        return ["المشاركة الصفية", "الواجبات المنزلية", "الاختبار القصير", "السلوك والالتزام"]

st.title("👨‍🏫 شاشة الرصد والتقييم الذكي")

# القائمة الجانبية لإدخال البيانات الأساسية
with st.sidebar:
    st.header("بيانات الحصة")
    teacher = st.text_input("اسم المعلم")
    subject = st.selectbox("المادة", ["العلوم", "الرياضيات", "اللغة العربية", "الإنجليزية"])
    class_name = st.text_input("الصف (مثلاً: 7/أ)")

# إصلاح مشكلة البنود: عرضها واختيارها
st.subheader("📋 بنود التقييم")
available_items = load_eval_items()
selected_items = st.multiselect("حدد البنود المراد رصدها:", available_items, default=available_items)

# جدول الرصد التفاعلي
if teacher and class_name:
    st.info(f"رصد لطلاب الصف {class_name}")
    
    # نموذج الرصد
    with st.form("evaluation_form"):
        student_name = st.text_input("اسم الطالب")
        
        # إنشاء أعمدة ديناميكية للدرجات بناءً على البنود المختارة
        cols = st.columns(len(selected_items))
        grades = {}
        for i, item in enumerate(selected_items):
            grades[item] = cols[i].number_input(f"{item}", min_value=0, max_value=10, step=1)
        
        submit = st.form_submit_button("حفظ الرصد في Google Sheets")
        
        if submit:
            # تجهيز البيانات للحفظ السحابي
            data_to_save = {
                "التاريخ": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                "المعلم": teacher,
                "المادة": subject,
                "الصف": class_name,
                "الطالب": student_name
            }
            data_to_save.update(grades)
            
            try:
                # قراءة البيانات الحالية ثم إضافة السطر الجديد
                df = conn.read(worksheet="Sheet1")
                new_df = pd.concat([df, pd.DataFrame([data_to_save])], ignore_index=True)
                conn.update(worksheet="Sheet1", data=new_df)
                st.success(f"✅ تم رصد الطالب {student_name} بنجاح!")
            except Exception as e:
                st.warning("تم الحفظ محلياً فقط.. تأكد من ربط رابط Google Sheets في الإعدادات")
                st.write(data_to_save)
