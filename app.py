import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Card Log System Online", layout="wide")

# --- 2. เชื่อมต่อ Google Sheets ---
# สำคัญ: เปลี่ยน URL เป็นลิงก์ Google Sheets ของคุณ
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1jphuWBQJ36hb3vtzCZnbmrbpNmj0MJ6yu869cj_sfS8/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def get_current_sheet_name():
    """สร้างชื่อชีตตามวันที่ปัจจุบัน (รูปแบบ: 7.05.69)"""
    now = datetime.now()
    return f"{now.day}.{now.month:02d}.{(now.year + 543) % 100}"

def get_safe_data(sheet_name):
    """ดึงข้อมูลจากชีตที่ระบุ ถ้าไม่มีให้คืนค่าตารางเปล่า"""
    required_cols = [
        'วันที่รับเคส', 'Freshdesk ID', 'รายละเอียด', 'ศูนย์บริการ', 
        'ต้องการแก้ไขข้อมูล', 'เจ้าหน้าที่แก้ไขข้อมูล', 'อนุมัติแก้หรือไม่', 'หมายเหตุ'
    ]
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, ttl="0")
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return pd.DataFrame(columns=required_cols)
        
        df.columns = [str(c).strip() for c in df.columns]
        for col in required_cols:
            if col not in df.columns:
                df[col] = "" 
        return df[required_cols]
    except:
        # ถ้าหาชีตไม่เจอ (เช่น เป็นวันใหม่ที่ยังไม่มีการบันทึก)
        return pd.DataFrame(columns=required_cols)

# --- 3. ข้อมูลตัวเลือก (Dropdown) ---
SELECT_TEXT = "--- กรุณาเลือก ---"
LOCATIONS = [SELECT_TEXT] + [  "One Bangkok", "กรุงเทพมหานคร 1 (สจก.2)", "กรุงเทพมหานคร 2 (สจก.5)", "กรุงเทพมหานคร 5 (สจก.9)", 
    "กรุงเทพมหานคร 6 (สจก.10)", "กรุงเทพมหานคร 4 (สจก.7)", "กรุงเทพมหานคร 3 (สจก.3)", "นนทบุรี", 
    "สมุทรสาคร", "สมุทรปราการ", "นครปฐม", "ราชบุรี", "เพชรบุรี", "ปทุมธานี", "พระนครศรีอยุธยา", 
    "สระบุรี", "สุพรรณบุรี", "ปราจีนบุรี", "ฉะเชิงเทรา", "ชลบุรี", "EEC จ.ชลบุรี", "ระยอง", "ตราด", 
    "จันทบุรี", "แรกรับ สระแก้ว", "ขอนแก่น", "นครราชสีมา", "แรกรับ หนองคาย", "แรกรับ มุกดาหาร", 
    "อุบลราชธานี", "แรกรับ ตาก", "ตาก", "เชียงใหม่", "เชียงราย", "แพร่", "กาญจนบุรี", 
    "นครศรีธรรมราช", "ชุมพร", "ประจวบคีรีขันธ์", "ภูเก็ต", "พังงา", "แรกรับ ระนอง", "ระนอง", 
    "สงขลา", "สุราษฎร์ธานี", "Truck1", "Truck2", "Truck3", "Truck4", "Truck5", "Truck6", 
    "Bus1", "Bus2", "ศูนย์กำกับ", "ไอทีสแควร์ ชั้น T"] # ใส่ชื่อเต็มตามเดิมของคุณได้เลย

STAFF_LIST = [SELECT_TEXT] + ["Patipol Phadungkiatpaisan ( พี )", "Pongsatorn Luangprasert ( บอส )", "Chananyu Wongkhongsan ( โอม )", 
    "Chanon Chaiwongka ( กาฟิว )", "Patthanapong Pamornphon ( เข้ม )", "Nitithorn Ratmaenching ( ป๊อบ )", 
    "Poramet Phisitsopakorn ( นิว )", "Sutiphong Kenda ( เคน )", "Tanawat Sinphoemthongphun ( หมู )", 
    "Supachai Leelapornsakul ( เหว่ย )"]

EDIT_LIST = [SELECT_TEXT] + ["แก้ไขชื่อ", "แก้ไขวันเกิด","แก้ไขชื่อและวันเกิด","แก้ไขสัญชาติ","แก้ไขประเภทงาน",
    "แก้ไขเลข Passpost","แก้ไขวันที่ออก / วันหมดอายุบัตร","วันหมดอายุหนังสือเดินทาง"]
STATUS_LIST = [SELECT_TEXT] + ["สามารถแก้ไขได้เลย", "อนุมัติ", "ไม่อนุมัติ"]

# --- 4. ส่วนหน้าจอหลัก ---
st.title("📝 ระบบบันทึก Log แก้ไขข้อมูลหน้าบัตร")

# ส่วนที่ 1: เพิ่มรายการใหม่ (จะไปลงชีตของวันนี้เสมอ)
with st.expander("➕ เพิ่มรายการใหม่", expanded=True):
    current_today_sheet = get_current_sheet_name()
    st.info(f"📍 ข้อมูลจะถูกบันทึกลงในชีต: **{current_today_sheet}**")
    
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
                
                # อ่านข้อมูลชีตวันนี้
                df_today = get_safe_data(current_today_sheet)
                df_updated = pd.concat([df_today, pd.DataFrame([new_row])], ignore_index=True)
                
                # บันทึก (ถ้าไม่มีชีต ระบบจะสร้างให้เอง)
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet=current_today_sheet, data=df_updated)
                st.success(f"✅ บันทึกข้อมูลลงชีต {current_today_sheet} สำเร็จ!")
                st.rerun()

# ส่วนที่ 2: แสดงรายการและ "แก้ไข"
st.divider()
selected_date = st.date_input("📅 เลือกวันที่เพื่อดู/แก้ไขข้อมูล", datetime.now())
view_sheet_name = f"{selected_date.day}.{selected_date.month:02d}.{(selected_date.year + 543) % 100}"

df_view = get_safe_data(view_sheet_name)

if not df_view.empty:
    # แสดงจากใหม่ไปเก่า
    for index, row in df_view.iloc[::-1].iterrows():
        with st.container(border=True):
            # แสดงข้อมูลสรุป
            c1, c2, c3 = st.columns([2, 5, 1])
            with c1:
                st.write(f"**ID:** {row['Freshdesk ID']}")
                st.caption(f"📅 {row['วันที่รับเคส']}")
            with c2:
                st.write(f"**สถานะ:** {row['อนุมัติแก้หรือไม่']} | **โดย:** {row['เจ้าหน้าที่แก้ไขข้อมูล']}")
                st.write(f"🔍 {row['ต้องการแก้ไขข้อมูล']} ({row['ศูนย์บริการ']})")
            with c3:
                # ปุ่มเปิดโหมดแก้ไข
                edit_btn = st.button("✏️ แก้ไข", key=f"edit_btn_{index}")
                if st.button("🗑️ ลบ", key=f"del_{index}"):
                    df_to_save = df_view.drop(index)
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet=view_sheet_name, data=df_to_save)
                    st.rerun()

            # ส่วนฟอร์มแก้ไข (จะปรากฏเมื่อกดปุ่มแก้ไข)
            if st.session_state.get(f"editing_{index}", False) or edit_btn:
                st.session_state[f"editing_{index}"] = True
                with st.form(key=f"edit_form_{index}"):
                    st.markdown("---")
                    st.write(f"🛠️ กำลังแก้ไขรายการ ID: {row['Freshdesk ID']}")
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        new_status = st.selectbox("เปลี่ยนสถานะ", STATUS_LIST, 
                                                 index=STATUS_LIST.index(row['อนุมัติแก้หรือไม่']) if row['อนุมัติแก้หรือไม่'] in STATUS_LIST else 0)
                        new_note = st.text_input("แก้ไขหมายเหตุ", value=row['หมายเหตุ'])
                    with col_e2:
                        new_staff = st.selectbox("เปลี่ยนเจ้าหน้าที่", STAFF_LIST, 
                                                index=STAFF_LIST.index(row['เจ้าหน้าที่แก้ไขข้อมูล']) if row['เจ้าหน้าที่แก้ไขข้อมูล'] in STAFF_LIST else 0)
                        new_detail = st.text_area("แก้ไขรายละเอียด", value=row['รายละเอียด'])
                    
                    if st.form_submit_button("💾 บันทึกการแก้ไข"):
                        df_view.at[index, 'อนุมัติแก้หรือไม่'] = new_status
                        df_view.at[index, 'หมายเหตุ'] = new_note
                        df_view.at[index, 'เจ้าหน้าที่แก้ไขข้อมูล'] = new_staff
                        df_view.at[index, 'รายละเอียด'] = new_detail
                        conn.update(spreadsheet=SPREADSHEET_URL, worksheet=view_sheet_name, data=df_view)
                        st.session_state[f"editing_{index}"] = False
                        st.success("อัปเดตข้อมูลแล้ว!")
                        st.rerun()
                    if st.form_submit_button("❌ ยกเลิก"):
                        st.session_state[f"editing_{index}"] = False
                        st.rerun()
else:
    st.info(f"📅 ยังไม่มีข้อมูลในชีต {view_sheet_name}")
