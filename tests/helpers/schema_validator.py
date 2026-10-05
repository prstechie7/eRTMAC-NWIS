"""
Schema, DDL, and Docker Configuration Validator for eRTMAC-NWIS.
Validates structural compliance of:
- docker/docker-compose.yml
- docker/init/01_schema.sql
"""

import os
import re
from typing import Dict, List, Set, Any


def get_project_root() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, "..", ".."))


def inspect_schema_sql(schema_path: str = None) -> Dict[str, Any]:
    """
    Parses and inspects 01_schema.sql for required tables, extensions,
    functions, triggers, and constraints.
    """
    if schema_path is None:
        schema_path = os.path.join(get_project_root(), "docker", "init", "01_schema.sql")

    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Search for extensions
    extensions = re.findall(r"CREATE\s+EXTENSION\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"']?([a-zA-Z0-9_\-]+)[\"']?", content, re.IGNORECASE)

    # Search for tables
    tables = re.findall(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)", content, re.IGNORECASE)

    # Search for functions
    functions = re.findall(r"CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([a-zA-Z0-9_]+)", content, re.IGNORECASE)

    # Search for hypertables
    hypertables = re.findall(r"create_hypertable\s*\(\s*['\"]([a-zA-Z0-9_]+)['\"]", content, re.IGNORECASE)

    # Search for check constraint hazard types
    hazard_types_match = re.search(r"chk_hazard_type\s+CHECK\s*\(\s*hazard_type\s+IN\s*\((.*?)\)\)", content, re.DOTALL | re.IGNORECASE)
    hazard_types = []
    if hazard_types_match:
        raw_types = hazard_types_match.group(1)
        hazard_types = [t.strip().strip("'\"") for t in raw_types.split(",") if t.strip()]

    # Indexes
    indexes = re.findall(r"CREATE\s+INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)", content, re.IGNORECASE)

    return {
        "file_exists": True,
        "path": schema_path,
        "content_length": len(content),
        "extensions": [e.lower() for e in extensions],
        "tables": [t.lower() for t in tables],
        "functions": [f.lower() for f in functions],
        "hypertables": [h.lower() for h in hypertables],
        "hazard_types": hazard_types,
        "indexes": indexes,
        "has_spatial_function": "find_offset_wells" in [f.lower() for f in functions],
        "has_vector_extension": "vector" in [e.lower() for e in extensions],
        "has_postgis_extension": "postgis" in [e.lower() for e in extensions],
        "has_timescaledb_extension": "timescaledb" in [e.lower() for e in extensions]
    }


def inspect_docker_compose(compose_path: str = None) -> Dict[str, Any]:
    """
    Parses docker-compose.yml to verify required services, ports, images, and healthchecks.
    """
    if compose_path is None:
        compose_path = os.path.join(get_project_root(), "docker", "docker-compose.yml")

    if not os.path.exists(compose_path):
        raise FileNotFoundError(f"Docker Compose file not found at: {compose_path}")

    with open(compose_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Search for top-level services
    # Regex searches service blocks
    services = re.findall(r"^\s{2}([a-zA-Z0-9_\-]+):\s*$", content, re.MULTILINE)

    # Search for ports
    ports = re.findall(r"[\"']?([0-9]{2,5}):([0-9]{2,5})[\"']?", content)

    # Check for timescale image
    has_timescale_image = "timescale/timescaledb-ha" in content

    return {
        "file_exists": True,
        "path": compose_path,
        "services": services,
        "has_db_service": "db" in services,
        "has_backend_service": "backend" in services,
        "has_frontend_service": "frontend" in services,
        "has_pgadmin_service": "pgadmin" in services,
        "exposed_ports": ports,
        "has_postgres_port": ("5432", "5432") in ports,
        "has_backend_port": ("8000", "8000") in ports,
        "has_frontend_port": ("3000", "3000") in ports,
        "has_timescale_image": has_timescale_image
    }
