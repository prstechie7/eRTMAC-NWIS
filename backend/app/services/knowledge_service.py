"""
Knowledge Repository Service for eRTMAC-NWIS.
Compliant with SIH26121 (Oil India Limited).
Enables structured multi-param search across historical events and source document evidence.
"""

from typing import List, Dict, Any, Optional
from app.models.schemas import ProvenanceType


class KnowledgeService:
    def __init__(self, db_data: Dict[str, Any]):
        self.db_data = db_data

    def search_knowledge(
        self,
        well: Optional[str] = None,
        field: Optional[str] = None,
        formation: Optional[str] = None,
        reservoir: Optional[str] = None,
        depth_min: Optional[float] = None,
        depth_max: Optional[float] = None,
        event: Optional[str] = None,
        severity: Optional[int] = None,
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        wells = self.db_data.get("wells", [])
        structured_events = []
        source_documents = []

        for w in wells:
            well_name = w.get("well_name", "")
            well_id = w.get("well_id", "")
            w_field = w.get("field_name", "")

            # Filter well / field
            if well and well.lower() not in well_name.lower() and well.lower() not in well_id.lower():
                continue
            if field and field.lower() not in w_field.lower():
                continue

            hazards = w.get("historical_hazards", [])
            for h in hazards:
                h_depth = float(h.get("depth_md_m", 0.0))
                h_formation = h.get("formation_name", "")
                h_event = h.get("hazard_type", h.get("event_type", ""))
                h_sev = int(h.get("severity_level", 3))
                h_cause = h.get("failure_cause", h.get("description", ""))
                h_mitigation = h.get("mitigation_action", h.get("mitigation", ""))

                # Apply filters
                if formation and formation.lower() not in h_formation.lower():
                    continue
                if depth_min is not None and h_depth < depth_min:
                    continue
                if depth_max is not None and h_depth > depth_max:
                    continue
                if event and event.lower() not in h_event.lower():
                    continue
                if severity is not None and h_sev < severity:
                    continue
                if keyword:
                    text_blob = f"{h_cause} {h_mitigation} {h_formation} {h_event}".lower()
                    if keyword.lower() not in text_blob:
                        continue

                event_record = {
                    "event_id": h.get("hazard_id", "haz-000"),
                    "well_id": well_id,
                    "well_name": well_name,
                    "field": w_field,
                    "depth_md_m": h_depth,
                    "formation_name": h_formation,
                    "event_type": h_event,
                    "severity": h_sev,
                    "npt_hours": h.get("npt_hours", 0.0),
                    "description": h_cause,
                    "mitigation": h_mitigation,
                    "report_reference": h.get("report_reference", "DDR-DOC-001"),
                    "provenance_type": ProvenanceType.SYNTHETIC.value
                }
                structured_events.append(event_record)

                # Matching document evidence
                doc_record = {
                    "document_id": f"doc-{h.get('hazard_id', '001')}",
                    "well_name": well_name,
                    "document_type": "DDR",
                    "file_name": f"{h.get('report_reference', 'DDR-REPORT')}.pdf",
                    "source": "Oil India Drilling Operations Knowledge Base",
                    "source_page": 4,
                    "source_excerpt": h_cause,
                    "provenance_type": ProvenanceType.SYNTHETIC.value
                }
                source_documents.append(doc_record)

        return {
            "query_status": "success",
            "matches_count": len(structured_events),
            "structured_events": structured_events,
            "source_documents": source_documents,
            "data_provenance": ProvenanceType.SYNTHETIC.value
        }
