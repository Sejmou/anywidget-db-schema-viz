from duckdb import DuckDBPyConnection
from typing import Any
from .types import Entity


def get_tables(conn: DuckDBPyConnection) -> dict[str, dict[str, Any]]:
    # TODO: construct a query that is less of a mindfuck than the stuff here lol

    # Get columns info with relevant fields
    columns = conn.execute(
        """
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns
    WHERE table_schema = 'main'
    ORDER BY table_name, ordinal_position
    """
    ).fetchall()

    # Optional: get foreign key info
    fks = conn.execute(
        """
    SELECT 
        tc.table_name AS table,
        kcu.column_name AS column,
        ccu.table_name AS foreign_table,
        ccu.column_name AS foreign_column
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema='main';
    """
    ).fetchall()

    # Organize FK info by table & column for quick lookup
    fk_map = {}
    for table, column, foreign_table, foreign_column in fks:
        fk_map.setdefault(table, {})[column] = {
            "entity": foreign_table,
            "attribute": foreign_column,
        }

    # Build output structure
    tables = {}
    for table, column, dtype in columns:
        tables.setdefault(table, {"name": table, "attributes": []})
        attr = {"name": column, "datatype": dtype.upper()}
        if table in fk_map and column in fk_map[table]:
            attr["foreign_key"] = fk_map[table][column]
        tables[table]["attributes"].append(attr)

    return {
        table["name"]: Entity.model_validate(table).model_dump(mode="json")
        for table in tables.values()
    }
