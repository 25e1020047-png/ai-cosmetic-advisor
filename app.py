import streamlit as st
import pandas as pd
from recommender import CosmeticRecommender

st.set_page_config(page_title="AI Cosmetic Advisor", page_icon="✨", layout="wide")

# Khởi tạo dữ liệu mẫu
@st.cache_resource
def load_engine():
    sample_data = pd.DataFrame([
        {"name": "Sữa rửa mặt Cerave Foaming Cleanser", "brand": "CeraVe", "category": "Cleanser",
         "gender": "Unisex", "skin_type": "Oily, Combination", "concerns": "acne oil control pores",
         "ingredients": "Ceramides Niacinamide Hyaluronic Acid", "price_vnd": 350000, "rating": 4.8},
        {"name": "Nước hoa hồng Klairs Supple Preparation", "brand": "Klairs", "category": "Toner",
         "gender": "Unisex", "skin_type": "Dry, Sensitive, All", "concerns": "hydration soothing redness",
         "ingredients": "Centella Asiatica Hyaluronic Acid Beta-Glucan", "price_vnd": 290000, "rating": 4.7},
        {"name": "Sữa rửa mặt nam Nivea Men Deep Rapid Acne", "brand": "Nivea Men", "category": "Cleanser",
         "gender": "Nam", "skin_type": "Oily", "concerns": "acne dark spots oil control",
         "ingredients": "Salicylic Acid Charcoal Himalayan Salt", "price_vnd": 95000, "rating": 4.5},
        {"name": "Serum La Roche-Posay Hyalu B5", "brand": "La Roche-Posay", "category": "Serum",
         "gender": "Nữ", "skin_type": "Dry, Sensitive", "concerns": "anti-aging hydration repair",
         "ingredients": "Hyaluronic Acid Vitamin B5 Madecassoside", "price_vnd": 850000, "rating": 4.9},
        {"name": "Kem chống nắng Anessa Perfect UV Milk", "brand": "Anessa", "category": "Sunscreen",
         "gender": "Unisex", "skin_type": "Oily, Combination, All", "concerns": "sun protection oil control",
         "ingredients": "Zinc Oxide Titanium Dioxide Hyaluronic Acid", "price_vnd": 520000, "rating": 4.8},
        {"name": "Serum L'Oreal Revitalift 1.5% Hyaluronic Acid", "brand": "L'Oreal", "category": "Serum",
         "gender": "Nữ", "skin_type": "Dry, Combination, All", "concerns": "anti-aging hydration wrinkles",
         "ingredients": "Hyaluronic Acid Vitamin C", "price_vnd": 420000, "rating": 4.6},
        {"name": "Gel dưỡng ẩm nam Clinique For Men Moisturizing", "brand": "Clinique", "category": "Moisturizer",
         "gender": "Nam", "skin_type": "Oily, Combination", "concerns": "hydration oil control",
         "ingredients": "Hyaluronic Acid Glycerin Silica", "price_vnd": 750000, "rating": 4.7}
    ])
    sample_data.to_csv("sample_cosmetics.csv", index=False)
    return CosmeticRecommender("sample_cosmetics.csv")

engine = load_engine()

# Khởi tạo trạng thái lưu hồ sơ người dùng (Onboarding)
if "profile_submitted" not in st.session_state:
    st.session_state.profile_submitted = False
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}

concern_map = {
    "Kiểm soát dầu & Mụn": "acne oil control pores",
    "Cấp ẩm & Phục hồi da": "hydration soothing repair",
    "Chống lão hóa & Nếp nhăn": "anti-aging wrinkles",
    "Chống nắng & Bảo vệ da": "sun protection"
}

# ==========================================
# MÀN HÌNH 1: PHẦN MỞ ĐẦU (CHÀO MỪNG & KHẢO SÁT)
# ==========================================
if not st.session_state.profile_submitted:
    st.markdown("<h1 style='text-align: center;'>✨ AI Cosmetic Advisor</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: gray;'>"
        "Trợ lý AI phân tích thành phần và cá nhân hóa chu trình chăm sóc da cho mọi giới tính"
        "</p>",
        unsafe_allow_html=True
    )
    st.divider()

    # Căn giữa form nhập thông tin
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        with st.container(border=True):
            st.subheader("📋 Thiết lập hồ sơ làn da của bạn")
            st.caption("Hãy cho AI biết một vài thông tin cơ bản để đề xuất sản phẩm chuẩn xác nhất.")

            with st.form("onboarding_form"):
                name = st.text_input("Tên của bạn *", placeholder="Ví dụ: Bảo Quyên, Minh Tuấn...")
                
                c1, c2 = st.columns(2)
                with c1:
                    age = st.number_input("Độ tuổi", min_value=12, max_value=80, value=20, step=1)
                with c2:
                    gender = st.selectbox("Giới tính", ["Unisex", "Nữ", "Nam", "Tất cả"])

                skin_type = st.selectbox(
                    "Loại da hiện tại của bạn",
                    ["Oily (Da dầu)", "Dry (Da khô)", "Combination (Da hỗn hợp)", "Sensitive (Da nhạy cảm)"]
                )
                concern_label = st.selectbox("Vấn đề da bạn muốn cải thiện nhất", list(concern_map.keys()))
                max_price = st.slider("Ngân sách tối đa cho mỗi sản phẩm (VNĐ)", 50000, 2000000, 600000, step=50000)

                submitted = st.form_submit_button("🚀 Bắt đầu tư vấn ngay", use_container_width=True, type="primary")

                if submitted:
                    st.session_state.user_profile = {
                        "name": name.strip() if name.strip() else "Bạn",
                        "age": age,
                        "gender": gender,
                        "skin_type": skin_type,
                        "skin_key": skin_type.split(" ")[0],
                        "concern_label": concern_label,
                        "max_price": max_price
                    }
                    st.session_state.profile_submitted = True
                    st.rerun()

# ==========================================
# MÀN HÌNH 2: TRANG TƯ VẤN & KẾT QUẢ CHÍNH
# ==========================================
else:
    profile = st.session_state.user_profile

    # Lời chào cá nhân hóa theo tên & độ tuổi
    st.title(f"👋 Xin chào, {profile['name']}!")
    
    # Gợi ý chuyên môn dựa trên độ tuổi
    if profile["age"] < 22:
        age_advice = "Ở độ tuổi dưới 22, làn da thường tiết nhiều dầu và dễ nổi mụn. Bạn nên ưu tiên làm sạch dịu nhẹ, cấp ẩm cơ bản và chống nắng đều đặn."
    elif 22 <= profile["age"] <= 28:
        age_advice = "Giai đoạn 22–28 tuổi là thời điểm vàng để bổ sung các chất chống oxy hóa (Vitamin C, Niacinamide) và duy trì hàng rào bảo vệ da."
    else:
        age_advice = "Ở độ tuổi trên 28, tốc độ tái tạo collagen giảm dần. Bạn nên tập trung vào các hoạt chất phục hồi chuyên sâu và chống lão hóa (Hyaluronic Acid, Peptides, Retinol)."

    st.info(f"💡 **Góc nhìn chuyên gia cho độ tuổi {profile['age']}:** {age_advice}")

    # Thanh bên (Sidebar) hiển thị tóm tắt hồ sơ & nút chỉnh sửa
    with st.sidebar:
        st.header("👤 Hồ sơ của bạn")
        st.write(f"**Tên:** {profile['name']}")
        st.write(f"**Tuổi:** {profile['age']} tuổi")
        st.write(f"**Giới tính:** {profile['gender']}")
        st.write(f"**Loại da:** {profile['skin_type']}")
        st.write(f"**Mục tiêu:** {profile['concern_label']}")
        st.write(f"**Ngân sách:** ≤ {profile['max_price']:,.0f} đ")
        
        st.divider()
        if st.button("✏️ Chỉnh sửa hồ sơ", use_container_width=True):
            st.session_state.profile_submitted = False
            st.rerun()

    # Hai tab tính năng chính
    tab1, tab2 = st.tabs(["🎯 Sản phẩm đề xuất cho bạn", "🧪 So sánh thành phần tương tự"])

    with tab1:
        st.subheader(f"Top sản phẩm phù hợp nhất ({profile['gender']} • Da {profile['skin_key']})")
        results = engine.recommend_by_profile(
            profile["gender"],
            profile["skin_key"],
            concern_map[profile["concern_label"]],
            profile["max_price"]
        )

        if results.empty:
            st.warning("Chưa tìm thấy sản phẩm khớp hoàn toàn với mức ngân sách này. Bạn hãy bấm 'Chỉnh sửa hồ sơ' ở thanh bên trái để tăng ngân sách nhé!")
        else:
            for _, row in results.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {row['name']} (`{row['brand']}`)")
                        st.write(f"**Phân loại:** {row['category']} | **Giới tính:** {row['gender']} | **Loại da:** {row['skin_type']}")
                        st.write(f"**Thành phần chính:** `{row['ingredients']}`")
                    with col2:
                        st.metric("Giá tham khảo", f"{row['price_vnd']:,.0f} đ")
                        st.write(f"⭐ Đánh giá: **{row['rating']}/5.0**")

    with tab2:
        st.subheader("Tìm sản phẩm thay thế có bảng thành phần tương tự (Cosine Similarity)")
        selected_prod = st.selectbox("Chọn một sản phẩm bạn đang dùng:", engine.df['name'].tolist())
        if st.button("Tìm sản phẩm tương tự"):
            sim_prods = engine.find_similar_products(selected_prod)
            for _, row in sim_prods.iterrows():
                st.info(f"**{row['name']}** ({row['brand']}) - Giá: {row['price_vnd']:,.0f} đ | Thành phần: {row['ingredients']}")