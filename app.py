
import streamlit as st
import requests
import datetime

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzd67eqgXFH_b82pnFrPsUlfgmPKto1mlp9rGgJUObVUqtx4cc0eDGFcBbbtmz4oMFnJg/exec"

def post_json(data):
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_json(params=None):
    try:
        response = requests.get(WEBHOOK_URL, params=params)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

st.set_page_config(page_title="ระบบแจ้งซ่อม MOTO24", page_icon="🛠️", layout="centered")
st.title("🛠️ ระบบแจ้งซ่อม MOTO24")

menu = st.sidebar.radio("เลือกเมนู", ["แจ้งซ่อม", "ตรวจสอบสถานะ", "สำหรับแอดมิน"])

if menu == "แจ้งซ่อม":
    st.subheader("📋 แบบฟอร์มแจ้งซ่อมอุปกรณ์")
    name = st.text_input("ชื่อผู้แจ้ง")
    branch = st.text_input("ชื่อบริษัท/สาขา")
    problem = st.text_area("ปัญหาที่พบ")
    reason = st.text_area("สาเหตุเบื้องต้น (ถ้าทราบ)")
    contact = st.text_input("ช่องทางติดต่อกลับ (เบอร์โทร/LINE)")
    images = st.text_area("ลิงก์รูปภาพประกอบ (ถ้ามี)", placeholder="สามารถใส่ได้หลายลิงก์คั่นด้วย , หรือ Enter")

    if st.button("ส่งแบบฟอร์ม"):
        if name and branch and problem and contact:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {
                "action": "submit",
                "name": name,
                "branch": branch,
                "problem": problem,
                "reason": reason,
                "contact": contact,
                "images": images,
                "date": now,
            }
            result = post_json(data)
            if result.get("status") == "success":
                st.success(f"แจ้งซ่อมสำเร็จ! รหัสงานของคุณคือ: {result.get('id', 'ไม่พบรหัส')}")
            else:
                st.error("เกิดข้อผิดพลาดในการส่งข้อมูล")
        else:
            st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")

elif menu == "ตรวจสอบสถานะ":
    st.subheader("ตรวจสอบสถานะงานซ่อม")
    code = st.text_input("กรอกรหัสงานซ่อม (เช่น Moto00001)")
    if st.button("เช็คสถานะ"):
        result = get_json(params={"action": "check", "id": code})
        if result and result.get("id"):
            st.success("พบข้อมูลของรหัสงานซ่อมนี้แล้ว")
            st.info(
                f"รหัส: {result.get('id', '')}
"
                f"ผู้แจ้ง: {result.get('name', '')}
"
                f"สาขา: {result.get('branch') or result.get('company', 'ไม่พบข้อมูล')}
"
                f"ปัญหา: {result.get('problem', '')}
"
                f"เหตุผล: {result.get('reason', '')}
"
                f"ติดต่อกลับ: {result.get('contact', '')}
"
                f"วันที่แจ้ง: {result.get('date', '')}
"
                f"สถานะ: {result.get('status', '')}"
            )
        else:
            st.warning("ไม่พบรหัสงานซ่อมนี้")

elif menu == "สำหรับแอดมิน":
    st.subheader("🔐 หน้าสำหรับแอดมิน")
    password = st.text_input("รหัสผ่าน", type="password")
    if password == "Admin123":
        data = get_json(params={"action": "all"})
        if isinstance(data, list):
            for case in data:
                st.markdown("---")
                st.write(f"รหัส: {case.get('id', '')}")
                st.write(f"ผู้แจ้ง: {case.get('name', '')}")
                st.write(f"สาขา: {case.get('branch') or case.get('company', '')}")
                st.write(f"ปัญหา: {case.get('problem', '')}")
                st.write(f"สถานะปัจจุบัน: {case.get('status', '')}")

                new_status = st.selectbox(f"เปลี่ยนสถานะของ {case.get('id', '')}", ["รอดำเนินการ", "กำลังดำเนินการ", "เสร็จสิ้น", "ยกเลิก"], key=case.get("id"))
                if st.button(f"อัปเดตสถานะ {case.get('id', '')}"):
                    update = post_json({"action": "update", "id": case.get("id", ""), "status": new_status})
                    if update.get("status") == "success":
                        st.success("อัปเดตสถานะเรียบร้อยแล้ว")
                    else:
                        st.error("อัปเดตไม่สำเร็จ")
        else:
            st.error("ไม่สามารถโหลดข้อมูลได้")
    elif password:
        st.error("รหัสผ่านไม่ถูกต้อง")
