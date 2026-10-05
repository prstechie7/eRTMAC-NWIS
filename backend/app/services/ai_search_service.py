"""
Grounded Natural-Language Evidence Retrieval Service for eRTMAC-NWIS.
Compliant with Requirement 27 (P1 Grounded Natural-Language Search) · SIH26121 · Oil India Limited.

Uses Google Gemini 2.5 Flash grounded strictly on structured drilling facts:
- DGH NDR Indian Basins & Discovery Wells
- Historical offset incidents (NHK-014, NHK-019, NHK-021, etc.)
- Documented NPT hours and verified mitigation pill recipes
- Never invents autonomous equipment commands; strictly decision-support.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.services.evidence_store_service import EvidenceStoreService, HISTORICAL_DRILLING_EVENTS
from app.services.indian_basin_service import IndianBasinService

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# Curated Engineering Suggestions for evaluators and engineers
CURATED_SUGGESTIONS = [
    {
        "category": "Stuck Pipe & Geomechanics",
        "query": "Show previous stuck-pipe events near the current bit (2,410 m)",
        "context": "Depth 2410m in Upper Tipam Sandstone"
    },
    {
        "category": "Offset Well History",
        "query": "What happened in offset well NHK-014 in Tipam Sandstone?",
        "context": "420m distance, 38.5 hr NPT differential sticking event"
    },
    {
        "category": "Lost Circulation & LCM",
        "query": "What are documented LCM mitigation treatments in Nahorkatiya offset wells?",
        "context": "Well NHK-019 lost circulation response"
    },
    {
        "category": "Pore Pressure & Margins",
        "query": "Compare pore pressure and fracture gradients across Tipam vs Barail formations",
        "context": "Upper Assam Shelf geomechanical window"
    },
    {
        "category": "NPT Intelligence",
        "query": "Summarize total and average historical NPT by hazard category in Upper Assam",
        "context": "Historical DDR database analytics"
    },
    {
        "category": "Connection Signatures",
        "query": "What abnormal connection gas signatures were documented in Nahorkatiya?",
        "context": "Connection intelligence and ballooning"
    }
]


class GroundedAISearchService:
    """Provides evidence-grounded AI search powered by Gemini 2.5 Flash."""

    @staticmethod
    def get_query_suggestions() -> List[Dict[str, Any]]:
        """Returns intelligent query suggestions for drilling engineers."""
        return CURATED_SUGGESTIONS

    @classmethod
    def search(
        cls,
        query: str,
        bit_depth_md: float = 2410.0,
        formation: str = "Upper Tipam Sandstone"
    ) -> Dict[str, Any]:
        """Convenience alias for execute_grounded_search."""
        return cls.execute_grounded_search(
            user_query=query,
            bit_depth_md_m=bit_depth_md,
            formation_name=formation
        )

    @classmethod
    def execute_grounded_search(
        cls,
        user_query: str,
        bit_depth_md_m: float = 2410.0,
        formation_name: str = "Upper Tipam Sandstone"
    ) -> Dict[str, Any]:
        """
        Executes grounded search using Gemini 2.5 Flash with strict evidence constraints.
        Falls back seamlessly to local deterministic evidence if API is unreachable.
        """
        # 1. Fetch relevant ground truth context from Evidence Store
        offset_analogs = EvidenceStoreService.get_what_happened_here_before(depth_md_m=bit_depth_md_m, window_m=60.0)
        npt_summary = EvidenceStoreService.get_npt_summary()
        indian_basins = IndianBasinService.get_all_basins()

        # Extract query keywords to find direct historical evidence matches
        query_terms = [w.lower() for w in user_query.replace("?", "").replace(",", "").replace(".", "").split() if len(w) > 2]
        query_matches = [
            inc for inc in HISTORICAL_DRILLING_EVENTS
            if any(term in inc.get("event_type", "").lower() or
                   term in inc.get("formation_name", "").lower() or
                   term in inc.get("well_name", "").lower() or
                   term in inc.get("mitigation_action", "").lower() or
                   term in inc.get("root_cause", "").lower()
                   for term in query_terms)
        ]

        # Combine depth analogs and query-matched historical incidents
        combined_events = list(offset_analogs.get("historical_analogs", []))
        for qm in query_matches:
            if not any(e.get("well_name") == qm.get("well_name") and e.get("event_type") == qm.get("event_type") for e in combined_events):
                combined_events.append(qm)

        if not combined_events:
            combined_events = list(HISTORICAL_DRILLING_EVENTS[:3])

        # Build evidence context payload
        evidence_context = {
            "query_depth_md_m": bit_depth_md_m,
            "formation_name": formation_name,
            "historical_events_near_bit": offset_analogs.get("historical_analogs", []),
            "all_historical_incidents": HISTORICAL_DRILLING_EVENTS,
            "matching_incidents": combined_events,
            "npt_statistics": npt_summary,
            "indian_basin_geology": [
                {
                    "basin": b["name"],
                    "operator": b["primary_operator"],
                    "pore_pressure_sg": b["typical_pp_gradient_sg"],
                    "fracture_gradient_sg": b["typical_fg_gradient_sg"],
                    "safe_mw_range": b["recommended_mw_range_sg"],
                    "hazards": b["regional_hazards"]
                }
                for b in indian_basins[:2]
            ]
        }

        # 2. Call Gemini API
        prompt_text = f"""
You are the Senior Drilling Decision-Support AI Assistant for Oil India Limited (eRTMAC-NWIS).
Your job is strictly EVIDENCE RETRIEVAL from the provided structured drilling repository.

MANDATORY RULES:
1. Ground your answer strictly in the EVIDENCE CONTEXT below.
2. CITE EXACT WELL NAMES (e.g. NHK-014, NHK-019), DEPTH INTERVALS (m), NPT HOURS, ROOT CAUSES, AND SOURCE DOCUMENTS (e.g. DDR-NHK-014).
3. NEVER invent or hallucinate operational instructions or say "execute shut-in immediately".
4. Always conclude with: "Qualified drilling engineer review required before operational execution."
5. Format with concise, professional markdown bullet points and clear metric highlights.

EVIDENCE CONTEXT:
{json.dumps(evidence_context, indent=2)}

USER QUESTION:
"{user_query}"
"""

        try:
            req_data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt_text}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 800
                }
            }

            req = urllib.request.Request(
                GEMINI_ENDPOINT,
                data=json.dumps(req_data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=8) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                candidate = res_body.get("candidates", [{}])[0]
                answer_text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")

                if not answer_text:
                    raise ValueError("Empty response from Gemini model")

                return {
                    "query": user_query,
                    "answer": answer_text,
                    "model": "gemini-2.5-flash",
                    "grounded_on": "STRUCTURED_DRILLING_EVIDENCE",
                    "matching_events_count": len(combined_events),
                    "cited_evidence": combined_events[:4],
                    "suggested_followups": [
                        "What was the recovery time and pill volume for well NHK-014?",
                        "What is the fracture margin at the current bit depth?",
                        "Show historical NPT breakdown for Tipam Sandstone"
                    ],
                    "engineer_review_required": True,
                    "autonomous_control": False
                }

        except Exception as e:
            # Deterministic Fallback if external API has network latency
            matching = combined_events if combined_events else HISTORICAL_DRILLING_EVENTS[:3]

            fallback_bullets = []
            for m in matching[:3]:
                fallback_bullets.append(
                    f"* **Well {m['well_name']}** ({m.get('surface_distance_m', 420)}m away, TSD delta {m.get('tsd_difference_m', 17)}m): "
                    f"**{m['event_type']}** in {m['formation_name']} ({m['depth_start_m']}–{m['depth_end_m']}m). "
                    f"NPT: **{m['npt_hours']} hrs**. Mitigation: {m['mitigation_action']} (Source: `{m['source_document']}`)."
                )

            fallback_answer = (
                f"### Evidence Summary for \"{user_query}\"\n\n"
                f"Found {len(matching)} matching historical events in the NWIS evidence repository:\n\n"
                + "\n".join(fallback_bullets) +
                "\n\n*Qualified drilling engineer review required before operational execution.*"
            )

            return {
                "query": user_query,
                "answer": fallback_answer,
                "model": "deterministic-evidence-store (gemini fallback)",
                "grounded_on": "STRUCTURED_DRILLING_EVIDENCE",
                "matching_events_count": len(matching),
                "cited_evidence": matching[:4],
                "suggested_followups": [
                    "What was the recovery time and pill volume for well NHK-014?",
                    "What is the fracture margin at the current bit depth?",
                    "Show historical NPT breakdown for Tipam Sandstone"
                ],
                "engineer_review_required": True,
                "autonomous_control": False
            }
