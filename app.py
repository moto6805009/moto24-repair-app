import streamlit as st
import requests

st.set_page_config(page_title="ระบบแจ้งซ่อม MOTO24", layout="centered")

# ----------------------
# CONFIG
# ----------------------
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzd67eqgXFH_b82pnFrPsUlfgmPKto1mlp9rGgJUObVUqtx4cc0eDGFcBbbtmz4oMFnJg/exec"
ADMIN_PASSWORD = "Admin123"

# ----------------------
# ฟังก์ชันสำหรับเชื่อม Webhook
# ----------------------
def post_json(payload):
    try:
        res = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        return res.json()
    except:
        return None

def get_json(params=None):
    try:
        res = requests.get(WEBHOOK_URL, params=params, timeout=10)
        return res.json()
    except:
        return None

# ----------------------
# UI
# ----------------------
st.title("🛠️ ระบบแจ้งซ่อม MOTO24")

menu = st.sidebar.radio("เลือกเมนู", ["แจ้งซ่อม", "ตรวจสอบสถานะ", "สำหรับแอดมิน"])

# ----------------------
# 1. แจ้งซ่อม
# ----------------------
if menu == "แจ้งซ่อม":
    st.subheader("📋 แบบฟอร์มแจ้งซ่อม")
    name = st.text_input("ชื่อผู้แจ้ง")
    company = st.text_input("ชื่อบริษัท / สาขา")
    problem = st.text_area("ปัญหาที่พบ")
    reason = st.text_area("เหตุผล/สาเหตุ (ถ้ามี)")
    contact = st.text_input("ช่องทางติดต่อ (เบอร์/ไลน์)")
    image_links = st.text_area("แนบลิงก์รูปภาพ (หากมี)", help="ใส่ลิงก์รูป Google Drive หรืออื่น ๆ")

    if st.button("ส่งข้อมูลแจ้งซ่อม"):
        if name and company and problem and contact:
            payload = {
                "action": "create",
                "name": name,
                "company": company,
                "problem": problem,
                "reason": reason,
                "contact": contact,
                "image_links": image_links
            }
            result = post_json(payload)
            if result and "id" in result:
                st.success(f"ส่งข้อมูลเรียบร้อยแล้ว ✅\n\nรหัส: {result.get('id', '')}")
            else:
                st.error("เกิดข้อผิดพลาดในการส่งข้อมูล")
        else:
            st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")

# ----------------------
# 2. ตรวจสอบสถานะ
# ----------------------
elif menu == "ตรวจสอบสถานะ":
    st.subheader("🔍 ตรวจสอบสถานะงานซ่อม")
    rid = st.text_input("กรอกรหัสงานซ่อมที่ได้รับ")
    if st.button("ตรวจสอบ"):
        if rid:
            data = get_json(params={"action": "check", "id": rid})
            if data and isinstance(data, dict):
                st.success("พบข้อมูลงานซ่อม")
                st.write(f"🔹 ชื่อผู้แจ้ง: {data.get('name', '-')}")
                st.write(f"🏢 บริษัท: {data.get('company', '-')}")
                st.write(f"🛠️ ปัญหา: {data.get('problem', '-')}")
                st.write(f"📄 เหตุผล: {data.get('reason', '-')}")
                st.write(f"📞 ติดต่อกลับ: {data.get('contact', '-')}")
                st.write(f"📸 แนบรูป: {data.get('image_links', '-')}")
                st.write(f"📌 สถานะล่าสุด: **{data.get('status', '-')}**")
            else:
                st.error("ไม่พบรหัสงานนี้")
        else:
            st.warning("กรุณากรอกรหัสงานซ่อม")

# ----------------------
# 3. แอดมิน
# ----------------------
elif menu == "สำหรับแอดมิน":
    st.subheader("เข้าสู่ระบบแอดมิน")
    password = st.text_input("รหัสผ่าน", type="password")
    if password == ADMIN_PASSWORD:
        st.success("เข้าสู่ระบบสำเร็จ")

        data = get_json(params={"action": "all"})
        if data:
            st.subheader("📄 รายการแจ้งซ่อมทั้งหมด")
            for row in reversed(data):
                rid = row.get('id', 'ไม่มีรหัส')
                name = row.get('name', '-')
                branch = row.get('branch', row.get('company', '-'))
                status = row.get('status', '-')
                st.info(f"{rid} | {name} | {branch} | สถานะ: {status}")

        st.markdown("---")
        st.subheader("🔄 อัปเดตสถานะงานซ่อม")
        rid = st.text_input("รหัสงานซ่อม")
        newstatus = st.selectbox("เลือกสถานะใหม่", ["รอดำเนินการ", "กำลังซ่อม", "เสร็จแล้ว", "ยกเลิก"])
        if st.button("อัปเดตสถานะ"):
            result = post_json({"action": "update", "id": rid, "status": newstatus})
            if result and result.get("status") == "updated":
                st.success("อัปเดตสถานะเรียบร้อยแล้ว")
            else:
                st.error("ไม่สามารถอัปเดตได้ หรือไม่พบรหัส")
    elif password:
        st.error("รหัสผ่านไม่ถูกต้อง")
