import os
import joblib
from typing import Dict, List
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.stem import SnowballStemmer
import psycopg2
from sqlalchemy import create_engine
from App import config

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

tokenizer = ToktokTokenizer()
russian_stopwords = stopwords.words('russian')
stemmer = SnowballStemmer('russian')


class SupportMeasureRecommender:
    def __init__(self, df=None, tfidf_matrix=None):
        self.df = df
        self.tfidf_matrix = tfidf_matrix
        self.tfidf = None
        if df is not None and tfidf_matrix is not None:
            self.load_models()

    def load_models(self):
        try:
            self.tfidf = joblib.load(os.path.join('App', 'ai', 'tfidf_vectorizer.joblib'))
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки TF-IDF векторайзера: {str(e)}")

    def recommend_measures(self, query, top_n=5):
        if self.tfidf is None or self.tfidf_matrix is None:
            raise RuntimeError("Модель не инициализирована")

        processed_query = self.preprocess_text(query)
        query_vector = self.tfidf.transform([processed_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)
        top_indices = np.argsort(similarities[0])[-top_n:][::-1]

        recommendations = []
        for idx in top_indices:
            recommendations.append({
                'Название': self.df.iloc[idx]['name'],
                'Описание': self.df.iloc[idx]['description'],
                'Условия': self.df.iloc[idx]['conditions'],
                'Период реализации': self.df.iloc[idx]['implementationPeriod'],
                'Ссылка': self.df.iloc[idx]['sourceLink'],
                'similarity_score': float(similarities[0][idx])
            })
        return recommendations

    @staticmethod
    def preprocess_text(text):
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', '', text)
        tokens = tokenizer.tokenize(text)
        tokens = [stemmer.stem(token) for token in tokens if token not in russian_stopwords]
        return ' '.join(tokens)


class RecommenderService:
    def __init__(self, model_path: str = None, tfidf_path: str = None):
        self.model_path = model_path or os.path.join('App', 'ai', 'recommender_model.joblib')
        self.tfidf_path = tfidf_path or os.path.join('App', 'ai', 'tfidf_matrix.joblib')
        self.recommender = None
        self.tfidf_matrix = None
        self.load_models()

    def load_models(self):
        try:
            df = self._load_data_from_db()
            self.tfidf_matrix = joblib.load(self.tfidf_path)
            self.recommender = SupportMeasureRecommender(df, self.tfidf_matrix)
            self.recommender.load_models()

        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки моделей: {str(e)}")

    def _load_data_from_db(self) -> pd.DataFrame:
        try:
            engine = create_engine(config.Config.SQLALCHEMY_DATABASE_URI)
            query = """
            SELECT 
                sm."idSupportMeasure",
                sm."name",
                sm."description",
                sm."condition",
                sm."implementationPeriod",
                sm."sourceLink",
                array_agg(DISTINCT i."industryName") AS industries,
                array_agg(DISTINCT c."categoryName") AS categories,
                array_agg(DISTINCT r."regionName") AS regions,
                array_agg(DISTINCT b."BRFName") AS business_forms
            FROM 
                "supportMeasures" sm
            LEFT JOIN "measure_industry" mi ON sm."idSupportMeasure" = mi."measureID"
            LEFT JOIN "industry" i ON mi."industryID" = i."idIndustry"
            LEFT JOIN "measureCategory" mc ON sm."idSupportMeasure" = mc."measureID"
            LEFT JOIN "category" c ON mc."categoryID" = c."idCategory"
            LEFT JOIN "measure_region" mr ON sm."idSupportMeasure" = mr."measureID"
            LEFT JOIN "region" r ON mr."regionID" = r."idRegion"
            LEFT JOIN "measure_brf" mb ON sm."idSupportMeasure" = mb."measureID"
            LEFT JOIN "business_registration_form" b ON mb."brfID" = b."idBRF"
            GROUP BY sm."idSupportMeasure"
        """

            df = pd.read_sql(query, engine)
            df['combined_text'] = df.apply(lambda x: ' '.join([
                x['name'] or '',
                x['description'] or '',
                x['condition'] or '',
                ' '.join(x['industries'] or []),
                ' '.join(x['categories'] or []),
                ' '.join(x['regions'] or []),
                ' '.join(x['business_forms'] or [])
            ]), axis=1)

            return df

        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки данных из БД: {str(e)}")

    def get_recommendations(self, input_data: Dict) -> List[Dict]:
        if not self.recommender:
            raise RuntimeError("Модель не загружена")

        query = self._build_query(input_data)
        recommendations = self.recommender.recommend_measures(query)

        if input_data.get('categories'):
            return self._filter_by_categories(recommendations, input_data['categories'])
        return recommendations[:5]

    def _build_query(self, input_data: Dict) -> str:
        query_parts = [
            " ".join(str(x) for x in input_data.get('regions', [])),
            " ".join(str(x) for x in input_data.get('business_forms', [])),
            input_data.get('support_purpose', ''),
            input_data.get('project_description', '')
        ]
        return " ".join(filter(None, query_parts))

    def _filter_by_categories(self, recommendations: List[Dict], categories: List[int]) -> List[Dict]:
        return [rec for rec in recommendations
                if any(cat['id'] in categories for cat in rec.get('Категория', []))][:5]

try:
    recommender_service = RecommenderService()
except Exception as e:
    print(f"ИИ-рекомендации недоступны: {str(e)}")
    recommender_service = None