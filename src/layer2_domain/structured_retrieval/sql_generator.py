"""Safe SQL generation for structured retrieval."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.structured import GeneratedSQL, StructuredQuery, StructuredQueryType


class SafeSQLGenerator:
    """Generate safe, parameterized SQL for a small allowlisted schema."""

    ALLOWED_AGGREGATIONS = {"COUNT", "SUM", "AVG", "MIN", "MAX"}
    DANGEROUS_PATTERNS = [
        r"\bDROP\b",
        r"\bDELETE\b",
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bTRUNCATE\b",
        r"\bALTER\b",
        r"\bCREATE\b",
        r"\bEXEC\b",
        r"\bUNION\b",
        r";\s*\w+",
        r"--",
        r"/\*",
    ]

    def __init__(self, allowed_tables: list[str], table_schemas: dict[str, list[str]]) -> None:
        self.allowed_tables = set(allowed_tables)
        self.table_schemas = table_schemas

    def generate(self, structured_query: StructuredQuery) -> GeneratedSQL:
        """Return generated SQL and its bound parameters."""
        warnings: list[str] = []
        if structured_query.target_table not in self.allowed_tables:
            return GeneratedSQL(
                query_id=structured_query.id,
                sql="",
                template_used="none",
                is_safe=False,
                safety_warnings=[f"Table '{structured_query.target_table}' not allowed"],
            )

        valid_columns = self.table_schemas.get(structured_query.target_table, [])
        columns = [column for column in structured_query.columns if column == "*" or column in valid_columns]
        for column in structured_query.columns:
            if column not in columns:
                warnings.append(f"Column '{column}' not in schema, ignoring")

        if structured_query.query_type == StructuredQueryType.AGGREGATION:
            sql, parameters = self._build_aggregation(structured_query)
        elif structured_query.query_type == StructuredQueryType.FILTER:
            sql, parameters = self._build_lookup(structured_query, columns)
        elif structured_query.query_type == StructuredQueryType.RANKING:
            sql, parameters = self._build_ranking(structured_query, columns)
        else:
            sql, parameters = self._build_lookup(structured_query, columns)

        is_safe = self._validate_sql(sql)
        if not is_safe:
            warnings.append("SQL failed safety validation")

        return GeneratedSQL(
            query_id=structured_query.id,
            sql=sql,
            template_used=structured_query.query_type.value,
            parameters=parameters,
            is_safe=is_safe,
            safety_warnings=warnings,
        )

    def _build_lookup(
        self,
        query: StructuredQuery,
        valid_columns: list[str],
    ) -> tuple[str, dict[str, object]]:
        columns = ", ".join(valid_columns) if valid_columns else "*"
        sql = f"SELECT {columns} FROM {query.target_table}"
        parameters: dict[str, object] = {}
        if query.filters:
            where_clause, parameters = self._build_where(query.target_table, query.filters)
            if where_clause:
                sql += f" WHERE {where_clause}"
        if query.limit:
            sql += f" LIMIT {int(query.limit)}"
        return sql, parameters

    def _build_aggregation(self, query: StructuredQuery) -> tuple[str, dict[str, object]]:
        agg_parts: list[str] = []
        valid_columns = set(self.table_schemas.get(query.target_table, []))
        for aggregation in query.aggregations:
            match = re.fullmatch(r"(\w+)\((\*|\w+)\)", aggregation.strip(), re.IGNORECASE)
            if match is None:
                continue
            function_name, column_name = match.groups()
            function_name = function_name.upper()
            if function_name not in self.ALLOWED_AGGREGATIONS:
                continue
            if column_name != "*" and column_name not in valid_columns:
                continue
            agg_parts.append(f"{function_name}({column_name})")
        if not agg_parts:
            agg_parts = ["COUNT(*)"]
        sql = f"SELECT {', '.join(agg_parts)} FROM {query.target_table}"
        parameters: dict[str, object] = {}
        if query.filters:
            where_clause, parameters = self._build_where(query.target_table, query.filters)
            if where_clause:
                sql += f" WHERE {where_clause}"
        return sql, parameters

    def _build_ranking(
        self,
        query: StructuredQuery,
        valid_columns: list[str],
    ) -> tuple[str, dict[str, object]]:
        sql, parameters = self._build_lookup(query, valid_columns)
        if query.order_by:
            order_by = query.order_by.strip()
            column_name = order_by.replace(" DESC", "").replace(" ASC", "").strip()
            if column_name in self.table_schemas.get(query.target_table, []):
                sql += f" ORDER BY {order_by}"
        return sql, parameters

    def _build_where(self, target_table: str, filters: dict[str, object]) -> tuple[str, dict[str, object]]:
        valid_columns = set(self.table_schemas.get(target_table, []))
        conditions: list[str] = []
        parameters: dict[str, object] = {}
        parameter_index = 0
        for column, value in filters.items():
            if column not in valid_columns:
                continue
            if isinstance(value, list):
                placeholders: list[str] = []
                for item in value:
                    key = f"p{parameter_index}"
                    parameter_index += 1
                    placeholders.append(f":{key}")
                    parameters[key] = item
                if placeholders:
                    conditions.append(f"{column} IN ({', '.join(placeholders)})")
                continue
            comparator = "="
            actual_value = value
            if column == "trust_score" and isinstance(value, (int, float)):
                comparator = ">="
            key = f"p{parameter_index}"
            parameter_index += 1
            conditions.append(f"{column} {comparator} :{key}")
            parameters[key] = actual_value
        return " AND ".join(conditions), parameters

    def _validate_sql(self, sql: str) -> bool:
        sql_upper = sql.upper()
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, sql_upper):
                return False
        return sql_upper.strip().startswith("SELECT")
