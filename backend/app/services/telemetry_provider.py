"""
Real-Time Telemetry Provider Adapters for eRTMAC-NWIS.
Compliant with SIH26121 (Oil India Limited).
Implements TelemetryProvider interface with Synthetic, CSV, and WITSML adapters.
"""

import os
import time
import math
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator, Optional
from app.models.schemas import ProvenanceType


class TelemetryProvider(ABC):
    @abstractmethod
    def get_current_snapshot(self) -> Dict[str, Any]:
        """Returns instantaneous 1 Hz drilling telemetry snapshot."""
        pass

    @abstractmethod
    async def stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Async generator streaming 1 Hz telemetry snapshots."""
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Returns health status of the provider adapter."""
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Returns metadata detailing provider capabilities and data provenance."""
        pass


class SyntheticTelemetryProvider(TelemetryProvider):
    def __init__(self, well_id: str = "c1f7a012-3b4c-4e89-9a11-000000000005", start_depth: float = 2410.0):
        self.well_id = well_id
        self.depth = start_depth
        self.start_time = time.time()

    def get_current_snapshot(self) -> Dict[str, Any]:
        tvdss = 2180.5 + (self.depth - 2410.0) * 0.99
        wob = 18.2
        torque = 12.8 if self.depth < 2413.0 else 15.4
        rpm = 95.0
        rop = 18.5 if self.depth < 2413.0 else 12.2
        area_bit = math.pi * (8.5 ** 2) / 4.0
        teale_mse = (wob * 1000.0 / area_bit) + (120.0 * math.pi * rpm * (torque * 1000.0 / 12.0)) / (area_bit * (rop * 3.28084))

        return {
            "timestamp": time.time(),
            "well_id": self.well_id,
            "depth_md": round(self.depth, 2),
            "tvdss": round(tvdss, 2),
            "ROP": rop,
            "WOB": wob,
            "RPM": rpm,
            "torque": torque,
            "hookload": 185.0,
            "standpipe_pressure": 2950.0,
            "pump_rate": 640.0,
            "mud_weight_in": 1.16,
            "mud_weight_out": 1.16,
            "ECD": 1.21,
            "pit_volume": 320.0,
            "flow_in": 640.0,
            "flow_out": 639.8,
            "teale_mse_psi": round(teale_mse, 0),
            "provenance_type": ProvenanceType.SYNTHETIC.value
        }

    async def stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        while True:
            self.depth += 0.1
            yield self.get_current_snapshot()
            await asyncio.sleep(1.0)

    def health(self) -> Dict[str, Any]:
        return {
            "provider": "SyntheticTelemetryProvider",
            "status": "HEALTHY",
            "active_well_id": self.well_id,
            "uptime_seconds": round(time.time() - self.start_time, 1)
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_type": "SYNTHETIC",
            "provenance_type": ProvenanceType.SYNTHETIC.value,
            "frequency_hz": 1.0,
            "description": "Deterministic calibrated synthetic WITSML telemetry stream for Upper Assam profile."
        }


class CSVTelemetryProvider(TelemetryProvider):
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.records = []
        self.index = 0
        if os.path.exists(csv_file_path):
            import csv
            with open(csv_file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.records.append(row)

    def get_current_snapshot(self) -> Dict[str, Any]:
        if not self.records:
            return {
                "timestamp": time.time(),
                "well_id": "CSV-DEMO-01",
                "depth_md": 2400.0,
                "provenance_type": ProvenanceType.PUBLIC.value
            }
        rec = self.records[self.index % len(self.records)]
        return {
            "timestamp": time.time(),
            "well_id": rec.get("well_id", "CSV-DEMO-01"),
            "depth_md": float(rec.get("depth_md", 2400.0)),
            "tvdss": float(rec.get("tvdss", 2200.0)),
            "ROP": float(rec.get("ROP", 15.0)),
            "WOB": float(rec.get("WOB", 18.0)),
            "RPM": float(rec.get("RPM", 90.0)),
            "torque": float(rec.get("torque", 12.0)),
            "hookload": float(rec.get("hookload", 180.0)),
            "standpipe_pressure": float(rec.get("standpipe_pressure", 2900.0)),
            "pump_rate": float(rec.get("pump_rate", 600.0)),
            "mud_weight_in": float(rec.get("mud_weight_in", 1.15)),
            "mud_weight_out": float(rec.get("mud_weight_out", 1.15)),
            "ECD": float(rec.get("ECD", 1.20)),
            "pit_volume": float(rec.get("pit_volume", 300.0)),
            "flow_in": float(rec.get("flow_in", 600.0)),
            "flow_out": float(rec.get("flow_out", 600.0)),
            "provenance_type": ProvenanceType.PUBLIC.value
        }

    async def stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        while True:
            yield self.get_current_snapshot()
            self.index += 1
            await asyncio.sleep(1.0)

    def health(self) -> Dict[str, Any]:
        return {
            "provider": "CSVTelemetryProvider",
            "status": "HEALTHY" if self.records else "NO_DATA",
            "file_path": self.csv_file_path,
            "total_records": len(self.records)
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_type": "CSV_FILE",
            "provenance_type": ProvenanceType.PUBLIC.value,
            "file": self.csv_file_path
        }


class WITSMLTelemetryProvider(TelemetryProvider):
    """
    WITSML Telemetry Provider Interface / Stub.
    Requires real OIL eRTMAC endpoint credentials to connect in production.
    """
    def __init__(self, endpoint: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        self.endpoint = endpoint or os.getenv("WITSML_ENDPOINT", "")
        self.username = username or os.getenv("WITSML_USERNAME", "")
        self.password = password or os.getenv("WITSML_PASSWORD", "")
        self.is_connected = bool(self.endpoint and self.username)

    def get_current_snapshot(self) -> Dict[str, Any]:
        if not self.is_connected:
            raise RuntimeError(
                "WITSML Provider not connected: Confidential Oil India operational endpoint credentials required. "
                "Use ERTMAC_PROVIDER=synthetic for demo mode."
            )
        return {
            "timestamp": time.time(),
            "well_id": "OIL-LIVE-01",
            "depth_md": 0.0,
            "provenance_type": ProvenanceType.OIL_INTERNAL.value
        }

    async def stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        if not self.is_connected:
            raise RuntimeError("WITSML Provider requires operational endpoint credentials.")
        yield self.get_current_snapshot()

    def health(self) -> Dict[str, Any]:
        return {
            "provider": "WITSMLTelemetryProvider",
            "status": "CONNECTED" if self.is_connected else "NOT_CONFIGURED",
            "endpoint": self.endpoint or "UNCONFIGURED"
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_type": "WITSML_LIVE",
            "provenance_type": ProvenanceType.OIL_INTERNAL.value,
            "endpoint_configured": self.is_connected
        }


def get_telemetry_provider() -> TelemetryProvider:
    provider_type = os.getenv("ERTMAC_PROVIDER", "synthetic").lower()
    if provider_type == "csv":
        return CSVTelemetryProvider(os.getenv("TELEMETRY_CSV_PATH", "data/demo/telemetry/telemetry_SYN-NHK-05.csv"))
    elif provider_type == "witsml":
        return WITSMLTelemetryProvider()
    return SyntheticTelemetryProvider()
