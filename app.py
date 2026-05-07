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

def get_data():
    """ฟังก์ชันหลักในการดึงข้อมูลจาก Google Sheets"""
    return conn.read(spreadsheet=SPREADSHEET_URL, ttl="0")

def update_gsheets(df_to_save):
    """ฟังก์ชันสำหรับบันทึกข้อมูลทับลงใน Google Sheets"""
    conn.update(spreadsheet=SPREADSHEET_URL, data=df_to_save)

def get_safe_data():
    """ฟังก์ชันดึงข้อมูลแบบปลอดภัย ตรวจสอบคอลัมน์ป้องกัน Error"""
    required_cols = [
        'วันที่รับเคส', 'Freshdesk ID', 'รายละเอียด', 'ศูนย์บริการ', 
        'ต้องการแก้ไขข้อมูล', 'เจ้าหน้าที่แก้ไขข้อมูล', 'อนุมัติแก้หรือไม่', 'หมายเหตุ'
    ]
    try:
        df = get_data()
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return pd.DataFrame(columns=required_cols)
            
        # ล้างชื่อคอลัมน์ ตัดช่องว่างที่อาจเผลอพิมพ์เกิน
        df.columns = [str(c).strip() for c in df.columns]
        
        # ตรวจสอบคอลัมน์ที่จำเป็น
        for col in required_cols:
            if col not in df.columns:
                df[col] = "" 
        
        return df[required_cols]
    except Exception as e:
        st.warning(f"⚠️ ระบบกำลังเชื่อมต่อหรือรอหัวตารางจาก Google Sheets: {e}")
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
                
                # ดึงข้อมูลปัจจุบันมาต่อท้าย (ตรวจสอบย่อหน้าตรงนี้ให้ดี)
                df_current = get_safe_data()
                df_updated = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True)
                update_gsheets(df_updated)
                st.success("✅ บันทึกข้อมูลเรียบร้อย!")
                st.rerun()

# ส่วนที่ 2: แสดงรายการและแก้ไข (Card UI)
st.divider()
st.subheader("🛠️ รายการล่าสุด")

df = get_safe_data()

if not df.empty:
    if st.button("🔄 Refresh ข้อมูล"):
        st.rerun()

    # เรียงลำดับเอาอันล่าสุดขึ้นก่อน
    df_display = df.iloc[::-1].copy()

    for index, row in df_display.iterrows():
        row_id = row['Freshdesk ID'] if pd.notna(row['Freshdesk ID']) else "N/A"
        row_status = row['อนุมัติแก้หรือไม่'] if pd.notna(row['อนุมัติแก้หรือไม่']) else "รอตรวจสอบ"
        
        status_icon = "🔵"
        if row_status == 'อนุมัติ': status_icon = "🟢"
        elif row_status == 'ไม่อนุมัติ': status_icon = "🔴"

        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 5, 1.5])
            with c1:
                st.markdown(f"**ID:** {row_id}")
                st.caption(f"📅 {row['วันที่รับเคส']}")
            with c2:
                st.markdown(f"{status_icon} **{row_status}**")
                st.write(f"📍 {row['ศูนย์บริการ']} | 👤 {row['เจ้าหน้าที่แก้ไขข้อมูล']}")
                st.info(f"📝 {row['รายละเอียด']}")
            with c3:
                if st.button("📝 แก้ไข", key=f"edit_{index}"):
                    st.session_state[f"edit_mode_{index}"] = True
                if st.button("🗑️ ลบ", key=f"del_{index}"):
                    df_to_save = df.drop(index)
                    update_gsheets(df_to_save)
                    st.rerun()

            # ฟอร์มแก้ไขภายใน Card
            if st.session_state.get(f"edit_mode_{index}", False):
                with st.form(key=f"form_{index}"):
                    st.write(f"✍️ แก้ไขเคส ID: {row_id}")
                    
                    try:
                        current_idx = STATUS_LIST.index(row_status)
                    except:
                        current_idx = 0
                        
                    new_status = st.selectbox("แก้ไขสถานะ", STATUS_LIST, index=current_idx)
                    new_note = st.text_input("แก้ไขหมายเหตุ", value=str(row['หมายเหตุ']) if pd.notna(row['หมายเหตุ']) else "")
                    
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
    st.info("💡 ยังไม่มีข้อมูลในระบบ หรือกำลังเชื่อมต่อข้อมูล...")
