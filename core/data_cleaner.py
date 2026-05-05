
import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional, Tuple, Dict

class DataCleaner:
    @staticmethod
    def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        initial_count = len(df)
        cleaned = df.drop_duplicates()
        removed_count = initial_count - len(cleaned)
        return cleaned, removed_count

    @staticmethod
    def fill_missing_values(df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
        df_copy = df.copy()
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
        non_numeric_cols = df_copy.select_dtypes(exclude=[np.number]).columns

        for col in numeric_cols:
            if strategy == 'mean':
                df_copy[col].fillna(df_copy[col].mean(), inplace=True)
            elif strategy == 'median':
                df_copy[col].fillna(df_copy[col].median(), inplace=True)
            elif strategy == 'mode':
                df_copy[col].fillna(df_copy[col].mode().iloc[0], inplace=True)
            elif strategy == 'zero':
                df_copy[col].fillna(0, inplace=True)

        for col in non_numeric_cols:
            df_copy[col].fillna(df_copy[col].mode().iloc[0], inplace=True)

        return df_copy

    @staticmethod
    def detect_outliers(df: pd.DataFrame, method: str = 'zscore', threshold: float = 3.0) -> pd.DataFrame:
        df_copy = df.copy()
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
        
        outliers = pd.DataFrame()
        
        for col in numeric_cols:
            if method == 'zscore':
                z_scores = np.abs(stats.zscore(df_copy[col].dropna()))
                col_outliers = df_copy[z_scores > threshold]
            elif method == 'iqr':
                q1 = df_copy[col].quantile(0.25)
                q3 = df_copy[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                col_outliers = df_copy[(df_copy[col] < lower_bound) | (df_copy[col] > upper_bound)]
            
            outliers = pd.concat([outliers, col_outliers]).drop_duplicates()
        
        return outliers

    @staticmethod
    def remove_outliers(df: pd.DataFrame, method: str = 'zscore', threshold: float = 3.0) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df_copy = df.copy()
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
        removed_outliers = pd.DataFrame()

        for col in numeric_cols:
            if method == 'zscore':
                z_scores = np.abs(stats.zscore(df_copy[col].dropna()))
                mask = z_scores <= threshold
            elif method == 'iqr':
                q1 = df_copy[col].quantile(0.25)
                q3 = df_copy[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                mask = (df_copy[col] >= lower_bound) & (df_copy[col] <= upper_bound)
            
            removed_outliers = pd.concat([removed_outliers, df_copy[~mask]]).drop_duplicates()
            df_copy = df_copy[mask]

        return df_copy, removed_outliers

    @staticmethod
    def standardize_format(df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()
        
        for col in df_copy.columns:
            if df_copy[col].dtype == 'object':
                try:
                    df_copy[col] = pd.to_datetime(df_copy[col])
                except (ValueError, TypeError):
                    try:
                        df_copy[col] = pd.to_numeric(df_copy[col], errors='ignore')
                    except:
                        pass
        
        df_copy.columns = [str(col).strip() for col in df_copy.columns]
        
        return df_copy

    @staticmethod
    def clean_data(df: pd.DataFrame, config: Optional[Dict] = None) -> Dict:
        if config is None:
            config = {
                'remove_duplicates': True,
                'fill_missing': True,
                'missing_strategy': 'mean',
                'remove_outliers': True,
                'outlier_method': 'zscore',
                'outlier_threshold': 3.0,
                'standardize': True
            }

        result = {
            'original': df,
            'cleaned': df.copy(),
            'removed_duplicates': 0,
            'removed_outliers': pd.DataFrame(),
            'info': []
        }

        if config.get('remove_duplicates'):
            result['cleaned'], removed = DataCleaner.remove_duplicates(result['cleaned'])
            result['removed_duplicates'] = removed
            result['info'].append(f"移除重复行: {removed} 行")

        if config.get('fill_missing'):
            strategy = config.get('missing_strategy', 'mean')
            result['cleaned'] = DataCleaner.fill_missing_values(result['cleaned'], strategy)
            result['info'].append(f"缺失值填充: 使用 {strategy} 策略")

        if config.get('remove_outliers'):
            method = config.get('outlier_method', 'zscore')
            threshold = config.get('outlier_threshold', 3.0)
            result['cleaned'], result['removed_outliers'] = DataCleaner.remove_outliers(
                result['cleaned'], method, threshold
            )
            result['info'].append(f"移除异常值: {len(result['removed_outliers'])} 行")

        if config.get('standardize'):
            result['cleaned'] = DataCleaner.standardize_format(result['cleaned'])
            result['info'].append("格式标准化完成")

        return result
