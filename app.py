import streamlit as st
import requests

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ช่องทางการแจ้งปัญหาระบบและอุปกรณ์ IT", layout="centered")
st.title("🖥️ ช่องทางการแจ้งปัญหาระบบและอุปกรณ์ IT")

# Webhook URL (ใส่ของคุณให้ถูกต้อง)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzd67eqgXFH_b82pnFrPsUlfgmPKto1mlp9rGgJUObVUqtx4cc0eDGFcBbbtmz4oMFnJg/exec"
ADMIN_PASSWORD = "Admin123"

# รายชื่อสาขา
branches = [
    "01-สำนักงานใหญ่", "02-ระโนด1", "03-สิงหนคร", "04-สทิงพระ", "05-ระโนด2", "06-บ่อล้อ",
    "07-หัวไทร", "08-ชะอวด", "09-ร่อนพิบูลย์", "10-หัวถนน", "11-ปากพนัง", "12-ลานสกา",
    "13-ท่าศาลา", "14-ร่อนพิบูลย์24", "15-บ่อล้อ24", "16-ทุ่งใหญ่24", "17-จันดี",
    "18-หัวไทร24", "19-สตูล24", "20-ฉลุง24", "21-ท่าแพ24", "22-ละงู24", "23-ชะอวด24",
    "24-นบพิตำ24", "25-พิปูน24", "26-ปากพนัง24", "27-ควนกาหลง24", "28-สทิงพระ24",
    "29-ระโนด24", "30-สิงหนคร24", "31-ท่าศาลา24", "32-รัตภูมิ 24", "33-หัวถนน24",
    "34-คูขวาง", "35-ควนหิน", "36-ควนหิน24", "37-บ้านด่าน24", "38-ทุ่งใหญ่", "39-บ้านด่าน24"
]

# เมนู
menu = st.sidebar.radio("📋 เลือกเมนู", ["แจ้งปัญหา", "ตรวจสอบสถานะ", "สำหรับแอดมิน"])

# ฟังก์ชันเชื่อมต่อ Webhook
def post_json(data):
    try:
        res = requests.post(WEBHOOK_URL, json=data)
        return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_json(params=None):
    try:
        res = requests.get(WEBHOOK_URL, params=params)
        return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ---------- หน้าแจ้งปัญหา ----------
if menu == "แจ้งปัญหา":
    st.subheader("📝 แจ้งปัญหาระบบหรืออุปกรณ์ IT")

    name = st.text_input("👤 ชื่อผู้แจ้ง")
    branch = st.selectbox("🏢 สาขา", branches)
    topic = st.text_area("📌 หัวข้อปัญหา")
    detail = st.text_area("🖊️ รายละเอียดเพิ่มเติม")
    contact = st.text_input("☎️ ช่องทางติดต่อกลับ")

    if st.button("✅ ส่งข้อมูล"):
        if name and branch and topic:
            payload = {
                "action": "add",
                "name": name,
                "company": branch,
                "problem": topic,
                "reason": detail,
                "contact": contact
            }
            result = post_json(payload)
            if result.get("status") == "success":
                st.success(f"🎉 แจ้งปัญหาสำเร็จ! รหัสของคุณคือ **{result['id']}**")
            else:
                st.error(f"❌ ไม่สามารถส่งข้อมูลได้: {result}")
        else:
            st.warning("⚠️ กรุณากรอกข้อมูลให้ครบ")

# ---------- ตรวจสอบสถานะ ----------
elif menu == "ตรวจสอบสถานะ":
    st.subheader("🔎 ตรวจสอบสถานะปัญหา")
    code = st.text_input("กรอกรหัสการแจ้ง (เช่น Moto00001)")
    if st.button("📥 ตรวจสอบ"):
        result = get_json(params={"action": "check", "id": code})
        if result and result.get("id"):
            st.success("✅ พบข้อมูลของรหัสนี้แล้ว")
            st.info(
                f"🧾 รหัส: {result['id']}\n"
                f"👤 ผู้แจ้ง: {result['name']}\n"
                f"🏢 สาขา: {result['company']}\n"
                f"📌 หัวข้อ: {result['problem']}\n"
                f"🖊️ รายละเอียด: {result['reason']}\n"
                f"☎️ ติดต่อกลับ: {result['contact']}\n"
                f"🕒 วันที่แจ้ง: {result['date']}\n"
                f"📊 สถานะ: {result['status']}"
            )
        else:
            st.warning("❗ ไม่พบรหัสนี้ในระบบ")

# ---------- สำหรับแอดมิน ----------
elif menu == "สำหรับแอดมิน":
    st.subheader("🔐 เข้าสู่ระบบแอดมิน")
    password = st.text_input("รหัสผ่าน", type="password")
    if password == ADMIN_PASSWORD:
        st.success("✅ เข้าสู่ระบบสำเร็จ")
        data = get_json(params={"action": "all"})
        if data and isinstance(data, list):
            for row in reversed(data):
                st.info(
                    f"{row['id']} | {row['name']} | สาขา: {row['company']} | สถานะ: {row['status']}"
                )
            st.markdown("---")
            st.subheader("🛠 อัปเดตสถานะ")
            rid = st.text_input("รหัสการแจ้ง")
            newstatus = st.selectbox("📊 สถานะใหม่", ["รอดำเนินการ", "กำลังดำเนินการ", "เสร็จแล้ว", "ยกเลิก"])
            if st.button("📤 อัปเดตสถานะ"):
                result = post_json({"action": "update", "id": rid, "status": newstatus})
                if result.get("status") == "updated":
                    st.success("✅ อัปเดตสถานะเรียบร้อยแล้ว")
                else:
                    st.error("❌ ไม่สามารถอัปเดตได้ หรือไม่พบรหัส")
    elif password:
        st.error("❌ รหัสผ่านไม่ถูกต้อง")
