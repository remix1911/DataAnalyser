
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, Any, Optional, Tuple

class MLModel:
    @staticmethod
    def cluster_kmeans(df: pd.DataFrame, n_clusters: int = 3, features: list = None) -> Tuple[pd.DataFrame, Dict]:
        if features is None:
            features = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(features) == 0:
            return df, {'error': '没有数值型特征'}
        
        try:
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(df[features])
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(scaled_data)
            
            df_result = df.copy()
            df_result['cluster'] = labels
            
            inertia = kmeans.inertia_
            
            return df_result, {
                'inertia': inertia,
                'cluster_centers': kmeans.cluster_centers_.tolist(),
                'n_clusters': n_clusters,
                'feature_importance': features
            }
        except Exception as e:
            return df, {'error': str(e)}

    @staticmethod
    def cluster_dbscan(df: pd.DataFrame, eps: float = 0.5, min_samples: int = 5, features: list = None) -> Tuple[pd.DataFrame, Dict]:
        if features is None:
            features = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(features) == 0:
            return df, {'error': '没有数值型特征'}
        
        try:
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(df[features])
            
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            labels = dbscan.fit_predict(scaled_data)
            
            df_result = df.copy()
            df_result['cluster'] = labels
            
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            
            return df_result, {
                'n_clusters': n_clusters,
                'noise_points': sum(labels == -1),
                'eps': eps,
                'min_samples': min_samples
            }
        except Exception as e:
            return df, {'error': str(e)}

    @staticmethod
    def classify(df: pd.DataFrame, target_col: str, features: list = None, 
                 model_type: str = 'random_forest') -> Dict[str, Any]:
        if target_col not in df.columns:
            return {'error': '目标列不存在'}
        
        if features is None:
            features = [col for col in df.columns if col != target_col and df[col].dtype in [np.int64, np.float64]]
        
        if len(features) == 0:
            return {'error': '没有可用的特征列'}
        
        try:
            X = df[features]
            y = df[target_col]
            
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            
            X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            if model_type == 'random_forest':
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            elif model_type == 'logistic':
                model = LogisticRegression(max_iter=1000, random_state=42)
            else:
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            
            return {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted'),
                'feature_importance': dict(zip(features, model.feature_importances_.tolist())),
                'model': model,
                'scaler': scaler,
                'label_encoder': le
            }
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def regress(df: pd.DataFrame, target_col: str, features: list = None, 
                model_type: str = 'random_forest') -> Dict[str, Any]:
        if target_col not in df.columns:
            return {'error': '目标列不存在'}
        
        if features is None:
            features = [col for col in df.columns if col != target_col and df[col].dtype in [np.int64, np.float64]]
        
        if len(features) == 0:
            return {'error': '没有可用的特征列'}
        
        try:
            X = df[features]
            y = df[target_col]
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            if model_type == 'random_forest':
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif model_type == 'linear':
                model = LinearRegression()
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            
            return {
                'mse': mean_squared_error(y_test, y_pred),
                'mae': mean_absolute_error(y_test, y_pred),
                'r2': r2_score(y_test, y_pred),
                'feature_importance': dict(zip(features, model.feature_importances_.tolist())),
                'model': model,
                'scaler': scaler
            }
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def predict(df: pd.DataFrame, model: Any, scaler: Any, features: list) -> pd.DataFrame:
        try:
            X = df[features]
            X_scaled = scaler.transform(X)
            predictions = model.predict(X_scaled)
            df_result = df.copy()
            df_result['prediction'] = predictions
            return df_result
        except Exception as e:
            return df
