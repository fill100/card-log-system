import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. ตั้งค่าการเชื่อมต่อ Google Sheets ---
# หมายเหตุ: URL ของไฟล์ Google Sheets ของคุณ
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1c_j-WUt3GfU-aGER-8T03-TD8QNrAmp4/edit?usp=sharing&ouid=109198691971293293321&rtpof=true&sd=true"

conn = st.connection("gsheets", type=GSheetsConnection)

def save_to_gsheets(data_dict):
    """บันทึกข้อมูลใหม่ลง Google Sheets"""
    # ดึงข้อมูลเดิมมาเพื่อหาจุดต่อท้าย
    existing_data = conn.read(spreadsheet=SPREADSHEET_URL, usecols=list(range(8)))
    existing_data = existing_data.dropna(how="all")
    
    new_df = pd.DataFrame([data_dict])
    updated_df = pd.concat([existing_data, new_df], ignore_index=True)
    
    # อัปเดตกลับไปยัง Google Sheets
    conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)

def update_gsheets_full(df_to_save):
    """ฟังก์ชันสำหรับแก้ไข/ลบ: บันทึกทับข้อมูลทั้งหมด"""
    conn.update(spreadsheet=SPREADSHEET_URL, data=df_to_save)

# --- แก้ไขในส่วน UI เดิม ---
# เปลี่ยนจาก save_to_excel(payload) เป็น save_to_gsheets(payload)
# เปลี่ยนจาก update_excel_file(df) เป็น update_gsheets_full(df)

# ในส่วนการดึงข้อมูลมาโชว์ (Preview) ให้ใช้:
# df = conn.read(spreadsheet=SPREADSHEET_URL)
# --- 3. ข้อมูลตัวเลือกต่างๆ ---
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

# --- 4. หน้าตาเว็บ UI ---
st.set_page_config(page_title="Card Log System", layout="wide")
st.title("📝 ระบบบันทึก Log แก้ไขข้อมูลการออกบัตร")

# ส่วนที่ 1: ฟอร์มเพิ่มข้อมูล
with st.expander("➕ เพิ่มรายการใหม่", expanded=True):
    with st.form("my_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            f_id = st.text_input("Freshdesk ID")
            center = st.selectbox("ศูนย์บริการ", LOCATIONS, index=0)
        with col2:
            edit_info = st.selectbox("ต้องการแก้ไขข้อมูล", EDIT_LIST, index=0)
            staff = st.selectbox("เจ้าหน้าที่แก้ไขข้อมูล", STAFF_LIST, index=0)
        with col3:
            status = st.selectbox("อนุมัติแก้หรือไม่", STATUS_LIST, index=0)
            note = st.text_input("หมายเหตุ")
        detail = st.text_area("รายละเอียด")
        
        if st.form_submit_button("🥷 บันทึกข้อมูล"):
            if SELECT_TEXT in [center, edit_info, staff, status] or not f_id or not detail.strip():
                st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วน")
            else:
                now = datetime.now()
                display_date = f"{now.day}/{now.month:02d}/{now.year + 543}"
                payload = {
                    'วันที่รับเคส': display_date, 'Freshdesk ID': f_id, 'รายละเอียด': detail,
                    'ศูนย์บริการ': center, 'ต้องการแก้ไขข้อมูล': edit_info,
                    'เจ้าหน้าที่แก้ไขข้อมูล': staff, 'อนุมัติแก้หรือไม่': status, 'หมายเหตุ': note
                }
                save_to_excel(payload)
                st.success("✅ บันทึกข้อมูลสำเร็จ!")
                st.rerun()

# ส่วนที่ 2: จัดการรายการ (UI แบบ Card)
if os.path.exists(FILE_NAME):
    st.divider()
    st.subheader("🛠️ รายการล่าสุด")
    
    try:
        xls = pd.ExcelFile(FILE_NAME)
        if xls.sheet_names:
            sheet_name = xls.sheet_names[-1]
            df = pd.read_excel(FILE_NAME, sheet_name=sheet_name)
            df_display = df.iloc[::-1].copy() # เอาล่าสุดขึ้นก่อน

            if st.button("🔄 Refresh ข้อมูล"):
                st.rerun()

            for index, row in df_display.iterrows():
                # ไอคอนสีตามสถานะ
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
                        # ปุ่มเปิดโหมดแก้ไข
                        if st.button("📝 แก้ไข", key=f"btn_edit_{index}"):
                            st.session_state[f"is_editing_{index}"] = True
                        
                        # ปุ่มลบ
                        if st.button("🗑️ ลบ", key=f"btn_del_{index}"):
                            df = df.drop(index)
                            update_excel_file(df) # เรียกใช้ฟังก์ชันที่ประกาศไว้ด้านบน
                            st.toast(f"ลบรายการ {row['Freshdesk ID']} สำเร็จ")
                            st.rerun()

                    # ฟอร์มแก้ไข (เมื่อกดปุ่มแก้ไข จะแสดงช่องให้แก้ครบทุกฟิลด์)
                    if st.session_state.get(f"is_editing_{index}", False):
                        with st.form(key=f"form_edit_{index}"):
                            st.write(f"✍️ แก้ไขข้อมูลรายการ ID: {row['Freshdesk ID']}")
                            
                            edit_col1, edit_col2 = st.columns(2)
                            
                            with edit_col1:
                                # แก้ไข Freshdesk ID และ รายละเอียด
                                new_f_id = st.text_input("แก้ไข Freshdesk ID", value=str(row['Freshdesk ID']))
                                
                                # แก้ไข ศูนย์บริการ (หา Index เดิม)
                                try: loc_idx = LOCATIONS.index(row['ศูนย์บริการ'])
                                except: loc_idx = 0
                                new_center = st.selectbox("แก้ไขศูนย์บริการ", LOCATIONS, index=loc_idx)
                                
                                # แก้ไข ประเภทการแก้ไข (หา Index เดิม)
                                try: edit_idx = EDIT_LIST.index(row['ต้องการแก้ไขข้อมูล'])
                                except: edit_idx = 0
                                new_edit_info = st.selectbox("แก้ไขประเภทงาน", EDIT_LIST, index=edit_idx)

                            with edit_col2:
                                # แก้ไข เจ้าหน้าที่ (หา Index เดิม)
                                try: staff_idx = STAFF_LIST.index(row['เจ้าหน้าที่แก้ไขข้อมูล'])
                                except: staff_idx = 0
                                new_staff = st.selectbox("แก้ไขเจ้าหน้าที่", STAFF_LIST, index=staff_idx)
                                
                                # แก้ไข สถานะ (หา Index เดิม)
                                try: stat_idx = STATUS_LIST.index(row['อนุมัติแก้หรือไม่'])
                                except: stat_idx = 0
                                new_status = st.selectbox("แก้ไขสถานะ", STATUS_LIST, index=stat_idx)
                                
                                new_note = st.text_input("แก้ไขหมายเหตุ", value=str(row['หมายเหตุ']) if pd.notna(row['หมายเหตุ']) else "")

                            new_detail = st.text_area("แก้ไขรายละเอียด", value=str(row['รายละเอียด']))

                            col_f1, col_f2 = st.columns([1, 1])
                            if col_f1.form_submit_button("💾 บันทึกการแก้ไข"):
                                # อัปเดตค่าลงใน DataFrame ตามตำแหน่ง Index เดิม
                                df.at[index, 'Freshdesk ID'] = new_f_id
                                df.at[index, 'รายละเอียด'] = new_detail
                                df.at[index, 'ศูนย์บริการ'] = new_center
                                df.at[index, 'ต้องการแก้ไขข้อมูล'] = new_edit_info
                                df.at[index, 'เจ้าหน้าที่แก้ไขข้อมูล'] = new_staff
                                df.at[index, 'อนุมัติแก้หรือไม่'] = new_status
                                df.at[index, 'หมายเหตุ'] = new_note
                                
                                update_excel_file(df)
                                st.session_state[f"is_editing_{index}"] = False
                                st.success("อัปเดตข้อมูลเรียบร้อย!")
                                st.rerun()
                                
                            if col_f2.form_submit_button("❌ ยกเลิก"):
                                st.session_state[f"is_editing_{index}"] = False
                                st.rerun()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
