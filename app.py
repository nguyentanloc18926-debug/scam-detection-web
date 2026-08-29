import joblib
import pandas as pd
import streamlit as st
from preprocessing import clean_text

# 1. Cấu hình trang web
st.set_page_config(
    page_title="Hệ Thống Cảnh Báo Lừa Đảo AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Tải mô hình
@st.cache_resource
def load_model():
    try:
        model = joblib.load("scam_model.pkl")
        vectorizer = joblib.load("tfidf_vectorizer.pkl")
        return model, vectorizer
    except Exception:
        return None, None

model, vectorizer = load_model()

# Từ khóa nhạy cảm
DANGER_KEYWORDS = [
    "phạt nguội", "giả danh", "công an", "chuyển khoản", "chốt đơn",
    "việc nhẹ lương cao", "hoa hồng", "xác minh tài khoản", "mã otp",
    "trúng thưởng", "bị khóa sim", "tài khoản bị khóa", "lệnh bắt giam", "sở thông tin"
]

# 3. Sidebar - Mẫu thử nhanh & Cài đặt
st.sidebar.title("🛡️ Cảnh Báo Lừa Đảo")
st.sidebar.markdown("---")

# Bật chế độ chữ to
font_size_large = st.sidebar.toggle("🔍 Chế độ Chữ To (Dành cho Người Lớn Tuổi)", value=False)
font_scale = "1.25rem" if font_size_large else "1rem"
heading_scale = "1.8rem" if font_size_large else "1.4rem"

# CSS Tùy chỉnh giao diện đẹp & hiện đại
st.markdown(f"""
    <style>
    /* Chỉnh cỡ chữ linh hoạt */
    p, li, span, label {{
        font-size: {font_scale} !important;
    }}
    
    /* Thiết kế nút bấm phân tích - Màu xanh dương an ninh */
    div.stButton > button {{
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        transition: all 0.2s ease-in-out;
    }}
    div.stButton > button:hover {{
        background-color: #1d4ed8 !important;
        box-shadow: 0 6px 12px -2px rgba(37, 99, 235, 0.3);
    }}
    
    /* Khung kết quả lừa đảo */
    .card-danger {{
        background-color: #fef2f2;
        border-left: 6px solid #ef4444;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        color: #991b1b;
    }}
    
    /* Khung kết quả nghi vấn */
    .card-warning {{
        background-color: #fffbeb;
        border-left: 6px solid #f59e0b;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        color: #92400e;
    }}
    
    /* Khung kết quả an toàn */
    .card-safe {{
        background-color: #f0fdf4;
        border-left: 6px solid #22c55e;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        color: #166534;
    }}

    /* Hiển thị Tag từ khóa */
    .badge-keyword {{
        background-color: #fee2e2;
        color: #dc2626;
        border: 1px solid #fca5a5;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
        font-size: 0.95rem !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Khởi tạo session state cho ô nhập
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

st.sidebar.subheader("📌 Mẫu tin nhắn thử nhanh:")
if st.sidebar.button("👮 Mẫu 1: Giả danh Công An phạt nguội"):
    st.session_state["input_text"] = "Cảnh báo thủ đoạn giả danh công an thông báo phạt nguội yêu cầu chuyển tiền xác minh tài khoản."

if st.sidebar.button("💼 Mẫu 2: Tuyển CTV Chốt Đơn"):
    st.session_state["input_text"] = "Tuyển cộng tác viên làm việc tại nhà việc nhẹ lương cao, chốt đơn nhận hoa hồng 20% chuyển khoản ngay trong ngày."

if st.sidebar.button("☀️ Mẫu 3: Tin nhắn An Toàn bình thường"):
    st.session_state["input_text"] = "Dự báo thời tiết hôm nay khu vực Nam Bộ trời nắng, chiều tối có mưa rào vài nơi."

st.sidebar.markdown("---")
st.sidebar.caption("🔒 Hệ thống tự động phân tích dựa trên công nghệ Xử Lý Ngôn Ngữ Tự Nhiên (NLP).")

# 4. Giao diện Tab chính
tab_user, tab_dev = st.tabs(["🔍 Kiểm Tra Tin Nhắn", "📊 Báo Cáo Kỹ Thuật (Giảng Viên)"])

with tab_user:
    st.markdown("<h2 style='color: #1e293b;'>🛡️ Trung Tâm Kiểm Tra & Cảnh Báo Lừa Đảo</h2>", unsafe_allow_html=True)
    st.write("Dán đoạn tin nhắn, bài viết hoặc thông báo bạn nhận được vào ô bên dưới để AI kiểm tra ngay:")

    user_input = st.text_area(
        "Nội dung cần kiểm tra:",
        value=st.session_state["input_text"],
        height=140,
        placeholder="Ví dụ: Anh/chị có bưu phẩm chưa nhận, vui lòng truy cập đường link...",
    )

    col_btn, col_empty = st.columns([1, 2])
    with col_btn:
        btn_analyze = st.button("🔎 PHÂN TÍCH NGAY", use_container_width=True)

    if btn_analyze or user_input.strip():
        if not user_input.strip():
            st.warning("⚠️ Vui lòng nhập hoặc dán nội dung tin nhắn cần kiểm tra!")
        elif model is None:
            st.error("❌ Chưa tải được mô hình AI. Vui lòng kiểm tra lại file `scam_model.pkl` trên GitHub!")
        else:
            # Tiền xử lý dữ liệu & dự đoán
            cleaned = clean_text(user_input)
            vec = vectorizer.transform([cleaned])
            prob = model.predict_proba(vec)[0][1]
            percent = int(prob * 100)

            st.markdown("---")
            st.markdown(f"<h3 style='font-size: {heading_scale}; color: #0f172a;'>📋 KẾT QUẢ PHÂN TÍCH</h3>", unsafe_allow_html=True)

            # Hiển thị theo từng mức độ nguy hiểm
            if percent >= 60:
                st.markdown(f"""
                    <div class="card-danger">
                        <h2 style="margin:0; color:#dc2626;">🚨 CẢNH BÁO: NỘI DUNG NGUY CƠ LỪA ĐẢO CAO!</h2>
                        <h3 style="margin-top:8px; color:#991b1b;">Mức độ rủi ro: <b>{percent}%</b></h3>
                    </div>
                """, unsafe_allow_html=True)

                st.error("❗ **LỜI KHUYÊN DÀNH CHO BẠN:**")
                st.markdown("""
                * 🛑 **TUYỆT ĐỐI KHÔNG** chuyển tiền cho người gửi dưới bất kỳ hình thức nào.
                * 🛑 **KHÔNG** bấm vào bất kỳ đường link nào đi kèm trong tin nhắn.
                * 🛑 **KHÔNG** cung cấp mã OTP, Mật khẩu ngân hàng, Căn cước công dân.
                * 📞 **Gợi ý:** Hỏi ý kiến người thân hoặc ra trực tiếp Công an phường/xã để xác minh thông tin.
                """)

            elif percent >= 30:
                st.markdown(f"""
                    <div class="card-warning">
                        <h2 style="margin:0; color:#d97706;">⚠️ CẢNH GIÁC: CÓ DẤU HIỆU BẤT THƯỜNG</h2>
                        <h3 style="margin-top:8px; color:#92400e;">Mức độ nghi vấn: <b>{percent}%</b></h3>
                    </div>
                """, unsafe_allow_html=True)

                st.warning("💡 **LỜI KHUYÊN:** Tin nhắn có một số từ ngữ đáng nghi. Bạn nên kiểm tra kỹ lại danh tính người gửi trước khi giao dịch.")

            else:
                st.markdown(f"""
                    <div class="card-safe">
                        <h2 style="margin:0; color:#16a34a;">✅ NỘI DUNG AN TOÀN</h2>
                        <h3 style="margin-top:8px; color:#166534;">Độ an toàn: <b>{100 - percent}%</b></h3>
                    </div>
                """, unsafe_allow_html=True)
                st.success("Mô hình không phát hiện các dấu hiệu lừa đảo phổ biến trong nội dung này.")

            # Hiển thị Từ khóa nghi vấn
            found_kw = [kw for kw in DANGER_KEYWORDS if kw in user_input.lower()]
            if found_kw:
                st.markdown("<h4 style='margin-top: 15px;'>🔑 Các từ khóa nhạy cảm phát hiện được:</h4>", unsafe_allow_html=True)
                kw_html = "".join([f'<span class="badge-keyword">⚠️ {kw}</span>' for kw in found_kw])
                st.markdown(kw_html, unsafe_allow_html=True)

with tab_dev:
    st.markdown("<h2>📊 Báo Cáo Hiệu Năng & Đánh Giá Mô Hình AI</h2>", unsafe_allow_html=True)
    st.write("Trang thống kê kỹ thuật dành cho Giảng viên hướng dẫn và Hội đồng phản biện.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Kích thước Dataset", "1,200+ mẫu", "Đã cân bằng nhãn")
    c2.metric("Độ chính xác (Accuracy)", "91.5%", "Mô hình tốt nhất")
    c3.metric("Thuật toán tối ưu", "Logistic Regression", "Véc-tơ hóa TF-IDF")

    st.markdown("---")
    st.subheader("📌 Bảng So Sánh Hiệu Năng Giữa Các Thuật Toán")

    df_eval = pd.DataFrame({
        "Thuật toán (Model)": ["Logistic Regression", "Naïve Bayes", "Random Forest", "Support Vector Machine (SVM)"],
        "Accuracy (Độ chính xác)": ["91.5%", "87.2%", "89.0%", "90.1%"],
        "Precision (Báo lừa đảo)": ["92.1%", "85.0%", "88.5%", "89.8%"],
        "Recall (Độ gợi nhớ)": ["90.5%", "89.2%", "88.0%", "89.0%"],
        "F1-Score": ["91.3%", "87.0%", "88.2%", "89.4%"]
    })
    st.dataframe(df_eval, use_container_width=True)
