
import pandas as pd
import json
import mysql.connector
from mysql.connector import Error
from typing import Optional

class DataLoader:
    @staticmethod
    def load_csv(file_path: str) -> Optional[pd.DataFrame]:
        try:
            return pd.read_csv(file_path, encoding='utf-8')
        except Exception as e:
            try:
                return pd.read_csv(file_path, encoding='gbk')
            except Exception as ex:
                return None

    @staticmethod
    def load_excel(file_path: str, sheet_name: str = 0) -> Optional[pd.DataFrame]:
        try:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            return None

    @staticmethod
    def load_json(file_path: str) -> Optional[pd.DataFrame]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                return pd.DataFrame([data])
            return None
        except Exception as e:
            return None

    @staticmethod
    def load_txt(file_path: str, delimiter: str = ',') -> Optional[pd.DataFrame]:
        try:
            return pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8')
        except Exception as e:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                if lines:
                    headers = lines[0].strip().split(delimiter)
                    data = [line.strip().split(delimiter) for line in lines[1:]]
                    return pd.DataFrame(data, columns=headers)
            except Exception as ex:
                return None
        return None

    @staticmethod
    def load_mysql(host: str, port: int, user: str, password: str, database: str, table: str) -> Optional[pd.DataFrame]:
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            if connection.is_connected():
                query = f"SELECT * FROM {table}"
                return pd.read_sql(query, connection)
        except Error as e:
            return None
        finally:
            if connection.is_connected():
                connection.close()
        return None

    @staticmethod
    def detect_file_type(file_path: str) -> str:
        lower_path = file_path.lower()
        if lower_path.endswith('.csv'):
            return 'csv'
        elif lower_path.endswith('.xlsx') or lower_path.endswith('.xls'):
            return 'excel'
        elif lower_path.endswith('.json'):
            return 'json'
        elif lower_path.endswith('.txt'):
            return 'txt'
        elif lower_path.endswith('.data'):
            return 'encrypted'
        return 'unknown'

    @staticmethod
    def load_file(file_path: str) -> Optional[pd.DataFrame]:
        file_type = DataLoader.detect_file_type(file_path)
        if file_type == 'csv':
            return DataLoader.load_csv(file_path)
        elif file_type == 'excel':
            return DataLoader.load_excel(file_path)
        elif file_type == 'json':
            return DataLoader.load_json(file_path)
        elif file_type == 'txt':
            return DataLoader.load_txt(file_path)
        return None
