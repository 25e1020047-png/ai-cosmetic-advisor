import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CosmeticRecommender:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        self._prepare_model()

    def _prepare_model(self):
        # Kết hợp thành phần và công dụng để tạo đặc trưng văn bản
        self.df['features'] = (
            self.df['ingredients'].fillna('') + ' ' + 
            self.df['concerns'].fillna('') + ' ' + 
            self.df['category'].fillna('')
        )
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['features'])
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

    def recommend_by_profile(self, gender, skin_type, concern, max_price, top_n=5):
        filtered = self.df.copy()

        # 1. Lọc theo giới tính (bao gồm cả sản phẩm Unisex)
        if gender != "Tất cả":
            filtered = filtered[filtered['gender'].isin([gender, 'Unisex'])]

        # 2. Lọc theo loại da
        filtered = filtered[
            filtered['skin_type'].str.contains(skin_type, case=False, na=False) |
            filtered['skin_type'].str.contains('All', case=False, na=False)
        ]

        # 3. Lọc theo ngân sách
        filtered = filtered[filtered['price_vnd'] <= max_price]

        # 4. Tính điểm phù hợp dựa trên vấn đề da (TF-IDF query)
        if concern and not filtered.empty:
            query_vec = self.tfidf.transform([concern])
            filtered_indices = filtered.index.tolist()
            sim_scores = cosine_similarity(query_vec, self.tfidf_matrix[filtered_indices]).flatten()
            filtered = filtered.assign(match_score=sim_scores)
            filtered = filtered.sort_values(by=['match_score', 'rating'], ascending=False)
        else:
            filtered = filtered.sort_values(by='rating', ascending=False)

        return filtered.head(top_n)

    def find_similar_products(self, product_name, top_n=4):
        if product_name not in self.df['name'].values:
            return pd.DataFrame()
        idx = self.df[self.df['name'] == product_name].index[0]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        product_indices = [i[0] for i in sim_scores]
        return self.df.iloc[product_indices]