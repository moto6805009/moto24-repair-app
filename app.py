import streamlit as st
import requests
import datetime

st.set_page_config(page_title="ระบบแจ้งซ่อม MOTO24", layout="wide")
st.sidebar.title("เลือกเมนู")
menu = st.sidebar.radio("", ["แจ้งซ่อม", "ตรวจสอบสถานะ", "สำหรับแอดมิน"])

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzd67eqgXFH_b82pnFrPsUlfgmPKto1mlp9rGgJUObVUqtx4cc0eDGFcBbbtmz4oMFnJg/exec"

if menu == "แจ้งซ่อม":
    st.header("📋 แบบฟอร์มแจ้งซ่อมอุปกรณ์")
    name = st.text_input("ชื่อผู้แจ้ง")
    issue = st.text_area("ปัญหาที่พบ")
    cause = st.text_area("เหตุผล/สาเหตุ (ถ้ามี)", "")
    contact = st.text_input("ช่องทางติดต่อ (เบอร์/ไลน์)")
    image_url = st.text_area("แนบลิงก์รูปภาพ (หากมี)", help="สามารถวาง URL ของรูปภาพจาก Google Drive หรือเว็บไซต์อื่น")

    if st.button("ส่งข้อมูลแจ้งซ่อม"):
        if name and issue and contact:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {
                "timestamp": now,
                "name": name,
                "issue": issue,
                "cause": cause,
                "contact": contact,
                "image_url": image_url,
                "status": "รอดำเนินการ"
            }
            try:
                res = requests.post(WEBHOOK_URL, json=data)
                if res.status_code == 200:
                    st.success("✅ ส่งข้อมูลเรียบร้อยแล้ว")
                else:
                    st.error("❌ เกิดข้อผิดพลาดในการส่งข้อมูล (Webhook Error)")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        else:
            st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")

elif menu == "ตรวจสอบสถานะ":
    st.header("🔍 ตรวจสอบสถานะงานซ่อม")
    code = st.text_input("กรอกรหัสงานซ่อม (เช่น Moto00001)")
    if st.button("ตรวจสอบ"):
        if code:
            try:
                res = requests.get(WEBHOOK_URL)
                if res.status_code == 200:
                    items = res.json().get("data", [])
                    found = False
                    for item in items:
                        if item["code"] == code:
                            st.success(f"📌 สถานะ: {item['status']}")
                            st.info(f"ปัญหา: {item['issue']}

ติดต่อ: {item['contact']}")
                            if item.get("image_url"):
                                st.image(item["image_url"], caption="แนบรูปภาพ", use_column_width=True)
                            found = True
                            break
                    if not found:
                        st.error("❌ ไม่พบรหัสงานซ่อมนี้")
                else:
                    st.error("❌ ไม่สามารถเชื่อมต่อข้อมูลได้")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")

elif menu == "สำหรับแอดมิน":
    st.header("🔐 เข้าสู่ระบบแอดมิน")
    password = st.text_input("รหัสผ่าน", type="password")
    if password == "Admin123":
        st.success("เข้าสู่ระบบสำเร็จ")
        try:
            res = requests.get(WEBHOOK_URL)
            if res.status_code == 200:
                items = res.json().get("data", [])
                for item in items:
                    st.markdown("---")
                    st.write(f"🆔 รหัส: {item['code']}")
                    st.write(f"👤 ชื่อ: {item['name']}")
                    st.write(f"📱 ติดต่อ: {item['contact']}")
                    st.write(f"🛠 ปัญหา: {item['issue']}")
                    st.write(f"📎 สถานะปัจจุบัน: `{item['status']}`")
                    if item.get("image_url"):
                        st.image(item["image_url"], width=300)
                    new_status = st.selectbox(f"เปลี่ยนสถานะสำหรับ {item['code']}", ["รอดำเนินการ", "กำลังดำเนินการ", "เสร็จสิ้น", "ยกเลิก"], index=["รอดำเนินการ", "กำลังดำเนินการ", "เสร็จสิ้น", "ยกเลิก"].index(item["status"]))
                    if st.button(f"อัปเดตสถานะ {item['code']}"):
                        update_data = {"code": item["code"], "new_status": new_status}
                        update_res = requests.post(WEBHOOK_URL, json=update_data)
                        if update_res.status_code == 200:
                            st.success("อัปเดตสถานะสำเร็จแล้ว")
                        else:
                            st.error("ไม่สามารถอัปเดตสถานะได้")
            else:
                st.error("❌ ไม่สามารถโหลดข้อมูลได้")
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")
    elif password:
        st.error("รหัสผ่านไม่ถูกต้อง")
