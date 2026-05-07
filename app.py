import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Card Log System Online", layout="wide")

# --- 2. เชื่อมต่อ Google Sheets ---
# สำคัญ: เปลี่ยน URL เป็นลิงก์ Google Sheets ของคุณ
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1c_j-WUt3GfU-aGER-8T03-TD8QNrAmp4/edit?usp=sharing&ouid=109198691971293293321&rtpof=true&sd=true"

conn = st.connection("gsheets", type=GSheetsConnection)

# ฟังก์ชันอ่านข้อมูล
def get_data():
    return conn.read(spreadsheet=SPREADSHEET_URL, ttl="0")

# ฟังก์ชันบันทึก/แก้ไขข้อมูลทั้งหมด
def update_gsheets(df_to_save):
    conn.update(spreadsheet=SPREADSHEET_URL, data=df_to_save)

# --- 3. ข้อมูลตัวเลือก (Dropdown) ---
SELECT_TEXT = "--- กรุณาเลือก ---"
LOCATIONS = [SELECT_TEXT] + ["One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "ไอทีสแควร์ ชั้น T"] 
STAFF_LIST = [SELECT_TEXT] + ["Patipol Phadungkiatpaisan ( พี )", "Chanon Chaiwongka ( กาฟิว )", "Nitithorn Ratmaenching ( ป๊อบ )"]
EDIT_LIST = [SELECT_TEXT] + ["แก้ไขชื่อ", "แก้ไขวันเกิด", "แก้ไขประเภทงาน"]
STATUS_LIST = [SELECT_TEXT] + ["สามารถแก้ไขได้เลย", "อนุมัติ", "ไม่อนุมัติ"]

# --- 4. ส่วนหน้าจอหลัก ---
st.title("📝 ระบบบันทึก Log ออนไลน์ (Google Sheets)")

# ส่วนที่ 1: เพิ่มรายการใหม่
with st.expander("➕ เพิ่มรายการใหม่", expanded=True):
    with st.form("my_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            f_id = st.text_input("Freshdesk ID")
            center = st.selectbox("ศูนย์บริการ", LOCATIONS)
        with col2:
            edit_info = st.selectbox("ต้องการแก้ไขข้อมูล", EDIT_LIST)
            staff = st.selectbox("เจ้าหน้าที่แก้ไขข้อมูล", STAFF_LIST)
        with col3:
            status = st.selectbox("อนุมัติแก้หรือไม่", STATUS_LIST)
            note = st.text_input("หมายเหตุ")
        detail = st.text_area("รายละเอียด")
        
        if st.form_submit_button("🚀 บันทึกข้อมูล"):
            if SELECT_TEXT in [center, edit_info, staff, status] or not f_id or not detail.strip():
                st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วน")
            else:
                now = datetime.now()
                display_date = f"{now.day}/{now.month:02d}/{now.year + 543}"
                new_row = {
                    'วันที่รับเคส': display_date, 'Freshdesk ID': f_id, 'รายละเอียด': detail,
                    'ศูนย์บริการ': center, 'ต้องการแก้ไขข้อมูล': edit_info,
                    'เจ้าหน้าที่แก้ไขข้อมูล': staff, 'อนุมัติแก้หรือไม่': status, 'หมายเหตุ': note
                }
                # อ่านข้อมูลเก่ามาต่อท้าย
                df = get_data()
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                update_gsheets(df)
                st.success("✅ บันทึกข้อมูลลง Google Sheets สำเร็จ!")
                st.rerun()

# ส่วนที่ 2: แสดงรายการและแก้ไข (Card UI)
st.divider()
st.subheader("🛠️ รายการล่าสุด (แก้ไข/ลบผ่าน Cloud)")

try:
    df = get_data()
    if not df.empty:
        df_display = df.iloc[::-1].copy() # ล่าสุดขึ้นก่อน

        if st.button("🔄 Refresh ข้อมูล"):
            st.rerun()

        for index, row in df_display.iterrows():
            status_icon = "🔵"
            if row['อนุมัติแก้หรือไม่'] == 'อนุมัติ': status_icon = "🟢"
            elif row['อนุมัติแก้หรือไม่'] == 'ไม่อนุมัติ': status_icon = "🔴"

            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 5, 1.5])
                with c1:
                    st.markdown(f"**ID:** {row['Freshdesk ID']}")
                    st.caption(f"📅 {row['วันที่รับเคส']}")
                with c2:
                    st.markdown(f"{status_icon} **{row['อนุมัติแก้หรือไม่']}**")
                    st.write(f"📍 {row['ศูนย์บริการ']} | 👤 {row['เจ้าหน้าที่แก้ไขข้อมูล']}")
                    st.info(f"📝 {row['รายละเอียด']}")
                with c3:
                    if st.button("📝 แก้ไข", key=f"edit_{index}"):
                        st.session_state[f"edit_mode_{index}"] = True
                    if st.button("🗑️ ลบ", key=f"del_{index}"):
                        df = df.drop(index)
                        update_gsheets(df)
                        st.rerun()

                # ฟอร์มแก้ไขภายใน Card
                if st.session_state.get(f"edit_mode_{index}", False):
                    with st.form(key=f"form_{index}"):
                        new_status = st.selectbox("แก้ไขสถานะ", STATUS_LIST, 
                                                 index=STATUS_LIST.index(row['อนุมัติแก้หรือไม่']) if row['อนุมัติแก้หรือไม่'] in STATUS_LIST else 0)
                        new_note = st.text_input("แก้ไขหมายเหตุ", value=row['หมายเหตุ'] if pd.notna(row['หมายเหตุ']) else "")
                        
                        col_f1, col_f2 = st.columns(2)
                        if col_f1.form_submit_button("💾 บันทึก"):
                            df.at[index, 'อนุมัติแก้หรือไม่'] = new_status
                            df.at[index, 'หมายเหตุ'] = new_note
                            update_gsheets(df)
                            st.session_state[f"edit_mode_{index}"] = False
                            st.rerun()
                        if col_f2.form_submit_button("❌ ยกเลิก"):
                            st.session_state[f"edit_mode_{index}"] = False
                            st.rerun()
    else:
        st.write("ยังไม่มีข้อมูลในระบบ")
except Exception as e:
    st.error(f"Error: {e}")
