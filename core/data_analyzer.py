
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, Optional

class DataAnalyzer:
    @staticmethod
    def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return pd.DataFrame()
        
        stats_df = df[numeric_cols].describe().T
        stats_df['median'] = df[numeric_cols].median()
        stats_df['mode'] = df[numeric_cols].mode().iloc[0]
        stats_df['skewness'] = df[numeric_cols].skew()
        stats_df['kurtosis'] = df[numeric_cols].kurt()
        stats_df['variance'] = df[numeric_cols].var()
        
        return stats_df

    @staticmethod
    def correlation_analysis(df: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return pd.DataFrame()
        
        try:
            return df[numeric_cols].corr(method=method)
        except Exception as e:
            return pd.DataFrame()

    @staticmethod
    def trend_analysis(df: pd.DataFrame, date_col: str, value_col: str, freq: str = 'D') -> pd.DataFrame:
        if date_col not in df.columns or value_col not in df.columns:
            return pd.DataFrame()
        
        df_copy = df.copy()
        try:
            df_copy[date_col] = pd.to_datetime(df_copy[date_col])
            df_copy.set_index(date_col, inplace=True)
            trend = df_copy[value_col].resample(freq).mean()
            trend = trend.reset_index()
            trend['rolling_mean'] = trend[value_col].rolling(window=7).mean()
            trend['rolling_std'] = trend[value_col].rolling(window=7).std()
            return trend
        except Exception as e:
            return pd.DataFrame()

    @staticmethod
    def pivot_analysis(df: pd.DataFrame, index_col: str, columns_col: str, values_col: str, 
                       aggfunc: str = 'sum') -> pd.DataFrame:
        try:
            return pd.pivot_table(df, index=index_col, columns=columns_col, 
                                 values=values_col, aggfunc=aggfunc, fill_value=0)
        except Exception as e:
            return pd.DataFrame()

    @staticmethod
    def dimension_analysis(df: pd.DataFrame, group_col: str, value_col: str) -> Dict[str, Any]:
        if group_col not in df.columns or value_col not in df.columns:
            return {}
        
        grouped = df.groupby(group_col)[value_col]
        
        result = {
            'group_counts': grouped.count().to_dict()
        }
        
        try:
            result['group_means'] = grouped.mean().to_dict()
        except Exception:
            result['group_means'] = "无法计算均值（非数值列）"
        
        try:
            result['group_sums'] = grouped.sum().to_dict()
        except Exception:
            result['group_sums'] = "无法计算求和（非数值列）"
        
        try:
            result['group_std'] = grouped.std().to_dict()
        except Exception:
            result['group_std'] = "无法计算标准差（非数值列）"
        
        try:
            result['group_min'] = grouped.min().to_dict()
        except Exception:
            result['group_min'] = "无法计算最小值"
        
        try:
            result['group_max'] = grouped.max().to_dict()
        except Exception:
            result['group_max'] = "无法计算最大值"
        
        return result

    @staticmethod
    def chi_square_test(df: pd.DataFrame, col1: str, col2: str) -> Dict[str, Any]:
        if col1 not in df.columns or col2 not in df.columns:
            return {}
        
        try:
            contingency_table = pd.crosstab(df[col1], df[col2])
            chi2, p, dof, expected = stats.chi2_contingency(contingency_table)
            
            return {
                'chi2_statistic': chi2,
                'p_value': p,
                'degrees_of_freedom': dof,
                'expected_frequencies': expected.tolist()
            }
        except Exception as e:
            return {}

    @staticmethod
    def t_test(df: pd.DataFrame, group_col: str, value_col: str) -> Dict[str, Any]:
        if group_col not in df.columns or value_col not in df.columns:
            return {}
        
        groups = df[group_col].unique()
        if len(groups) != 2:
            return {}
        
        group1 = df[df[group_col] == groups[0]][value_col]
        group2 = df[df[group_col] == groups[1]][value_col]
        
        try:
            t_stat, p_val = stats.ttest_ind(group1, group2)
            return {
                't_statistic': t_stat,
                'p_value': p_val,
                'group1_mean': group1.mean(),
                'group2_mean': group2.mean(),
                'group1_std': group1.std(),
                'group2_std': group2.std()
            }
        except Exception as e:
            return {}

    @staticmethod
    def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
        result = {
            'descriptive': DataAnalyzer.descriptive_statistics(df),
            'correlation': DataAnalyzer.correlation_analysis(df),
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_count': df.isnull().sum().to_dict(),
            'duplicate_count': df.duplicated().sum()
        }
        return result
