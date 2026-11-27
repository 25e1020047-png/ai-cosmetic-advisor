import streamlit as st
import pandas as pd
from recommender import CosmeticRecommender

st.set_page_config(page_title="AI Cosmetic Advisor", page_icon="✨", layout="wide")

# Khởi tạo dữ liệu mẫu nếu chưa có file CSV
@st.cache_resource
def load_engine():
    # Bạn có thể thay bằng đường dẫn 'data/cosmetics.csv' thực tế
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
         "ingredients": "Zinc Oxide Titanium Dioxide Hyaluronic Acid", "price_vnd": 520000, "rating": 4.8}
    ])
    sample_data.to_csv("sample_cosmetics.csv", index=False)
    return CosmeticRecommender("sample_cosmetics.csv")

engine = load_engine()

st.title("✨ Hệ Thống Tư Vấn Mỹ Phẩm Thông Minh (AI Cosmetic Advisor)")
st.markdown("Gợi ý sản phẩm cá nhân hóa theo **Giới tính, Loại da, Vấn đề da** và **Thành phần hoạt chất**.")

# Sidebar nhập thông tin người dùng
with st.sidebar:
    st.header("🔍 Hồ sơ làn da của bạn")
    gender = st.selectbox("Giới tính", ["Unisex", "Nam", "Nữ", "Tất cả"])
    skin_type = st.selectbox("Loại da", ["Oily (Da dầu)", "Dry (Da khô)", "Combination (Hỗn hợp)", "Sensitive (Nhạy cảm)"])
    skin_key = skin_type.split(" ")[0]
    
    concern_map = {
        "Kiểm soát dầu & Mụn": "acne oil control pores",
        "Cấp ẩm & Phục hồi": "hydration soothing repair",
        "Chống lão hóa": "anti-aging wrinkles",
        "Chống nắng bảo vệ da": "sun protection"
    }
    concern_label = st.selectbox("Vấn đề quan tâm nhất", list(concern_map.keys()))
    max_price = st.slider("Ngân sách tối đa (VNĐ)", 50000, 2000000, 600000, step=50000)

# Tab chức năng
tab1, tab2 = st.tabs(["🎯 Gợi ý theo hồ sơ da", "🧪 Tìm sản phẩm tương tự thành phần"])

with tab1:
    st.subheader(f"Top sản phẩm phù hợp cho {gender} - Da {skin_key}")
    results = engine.recommend_by_profile(gender, skin_key, concern_map[concern_label], max_price)
    
    if results.empty:
        st.warning("Không tìm thấy sản phẩm khớp hoàn toàn với mức ngân sách này. Hãy thử tăng ngân sách!")
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