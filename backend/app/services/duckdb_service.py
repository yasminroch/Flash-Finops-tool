import duckdb
import pandas as pd
import os
from ..config import get_settings


class DuckDBService:
    """Duckdb data source for the Flash Analytics mvp"""

    def __init__(self):
        self._conn = duckdb.connect(":memory:")
        self._load_data()

    def _load_data(self):
        """Load CSV data into DuckDB tables"""
        settings = get_settings()
        data_path = os.path.abspath(settings.data_path)

        # Load contract costs
        costs_path = os.path.join(
            data_path, "foundations.metabase.contract_metabase_costs.csv"
        )
        if os.path.exists(costs_path):
            df = pd.read_csv(costs_path)
            # Parse Brazilian currency format
            df["valor_clean"] = (
                df["valor"]
                .fillna("$0,00")
                .str.replace("$", "", regex=False)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
                .astype(float)
            )
            # Parse date dd-mm-yyyy
            df["data_parsed"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
            self._conn.execute(
                "CREATE TABLE contract_costs AS SELECT * FROM df"
            )

        # Load users
        users_path = os.path.join(
            data_path, "foundations.metabase.dim_metabase_users.csv"
        )
        if os.path.exists(users_path):
            df = pd.read_csv(users_path)
            # Clean metabase_user_id - remove dots used as thousands separator
            df["metabase_user_id"] = (
                df["metabase_user_id"]
                .astype(str)
                .str.replace(".", "", regex=False)
                .astype(int)
            )
            self._conn.execute(
                "CREATE TABLE dim_users AS SELECT * FROM df"
            )

        # Load activity
        activity_path = os.path.join(
            data_path, "foundations.metabase.flat_metabase_user_activity_daily.csv"
        )
        if os.path.exists(activity_path):
            df = pd.read_csv(activity_path)
            df["date_parsed"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
            self._conn.execute(
                "CREATE TABLE user_activity AS SELECT * FROM df"
            )

    def execute_query(self, sql: str) -> pd.DataFrame:
        """Execute a sql query and return a dataframe"""
        try:
            result = self._conn.execute(sql).df()
            return result
        except Exception as e:
            raise ValueError(f"Query error: {str(e)}")

    def load_dataframe(self, table_name: str, df: pd.DataFrame):
        """Load a DataFrame as a new table (or replace existing)."""
        try:
            self._conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        except:
            pass
        self._conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        print(f"[DuckDB] Loaded table '{table_name}' with {len(df)} rows")

    def get_schema_info(self) -> str:
        """Get schema information for LLM context."""
        tables = self._conn.execute("SHOW TABLES").df()
        schema_parts = []

        for table_name in tables["name"]:
            cols = self._conn.execute(
                f"DESCRIBE {table_name}"
            ).df()
            col_info = ", ".join(
                [f"{row['column_name']} ({row['column_type']})"
                 for _, row in cols.iterrows()]
            )
            schema_parts.append(f"Table: {table_name}\n  Columns: {col_info}")

        return "\n\n".join(schema_parts)


# Singleton instance
_db_service: DuckDBService | None = None


def get_db_service() -> DuckDBService:
    global _db_service
    if _db_service is None:
        _db_service = DuckDBService()
    return _db_service
