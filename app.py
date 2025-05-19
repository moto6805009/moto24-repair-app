import streamlit as st
import requests

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzd67eqgXFH_b82pnFrPsUlfgmPKto1mlp9rGgJUObVUqtx4cc0eDGFcBbbtmz4oMFnJg/exec"
ADMIN_PASSWORD = "Admin123"

st.set_page_config(page_title="ระบบแจ้งซ่อม MOTO24", layout="centered")
st.title("ระบบแจ้งซ่อม MOTO24")

menu = st.sidebar.radio("เลือกเมนู", ["แจ้งซ่อม", "ตรวจสอบสถานะ", "สำหรับแอดมิน"])

def post_json(data):
    try:
        res = requests.post(WEBHOOK_URL, json=data)
        return res.json()
    except:
        return None

def get_json(params=None):
    try:
        res = requests.get(WEBHOOK_URL, params=params)
        return res.json()
    except:
        return None

if menu == "แจ้งซ่อม":
    st.subheader("แจ้งซ่อมอุปกรณ์")
    name = st.text_input("ชื่อผู้แจ้ง")
    branch = st.text_input("สาขา")
    problem = st.text_area("ปัญหา")
    reason = st.text_area("เหตุผล")
    contact = st.text_input("ช่องทางติดต่อกลับ")
    if st.button("ส่งข้อมูล"):
        if name and branch and problem:
            payload = {
                "action": "add",
                "name": name,
                "branch": branch,
                "problem": problem,
                "reason": reason,
                "contact": contact,
                "img_urls": ""  # ยังไม่รองรับภาพ
            }
            result = post_json(payload)
            if result and result.get("status") == "success":
                st.success(f"แจ้งซ่อมสำเร็จ! รหัสของคุณคือ {result['id']}")
            else:
                st.error("ไม่สามารถส่งข้อมูลได้")
        else:
            st.warning("กรุณากรอกข้อมูลให้ครบ")

elif menu == "ตรวจสอบสถานะ":
    st.subheader("ตรวจสอบสถานะงานซ่อม")
    code = st.text_input("กรอกรหัสงานซ่อม (เช่น Moto00001)")
    if st.button("เช็คสถานะ"):
        result = get_json(params={"action": "check", "id": code})
        if result and result.get("id"):
            st.success("พบข้อมูลของรหัสงานซ่อมนี้แล้ว")
            st.info(
                f"รหัส: {result['id']}\n"
                f"ผู้แจ้ง: {result['name']}\n"
                f"สาขา: {result['branch']}\n"
                f"ปัญหา: {result['problem']}\n"
                f"เหตุผล: {result['reason']}\n"
                f"ติดต่อกลับ: {result['contact']}\n"
                f"วันที่แจ้ง: {result['date']}\n"
                f"สถานะ: {result['status']}"
            )
        else:
            st.warning("ไม่พบรหัสงานซ่อมนี้")

elif menu == "สำหรับแอดมิน":
    st.subheader("เข้าสู่ระบบแอดมิน")
    password = st.text_input("รหัสผ่าน", type="password")
    if password == ADMIN_PASSWORD:
        st.success("เข้าสู่ระบบสำเร็จ")
        data = get_json(params={"action": "all"})
        if data:
            for row in reversed(data):
                st.info(f"{row['id']} | {row['name']} | {row['branch']} | สถานะ: {row['status']}")
            st.markdown("---")
            st.subheader("อัปเดตสถานะงานซ่อม")
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
