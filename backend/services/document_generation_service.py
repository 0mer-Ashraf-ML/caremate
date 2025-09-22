# backend/services/document_generation_service.py
import os
import json
from typing import Dict, Any
from datetime import datetime, date
from backend.services.document_service import DocumentService
from backend.services.template_service import TemplateService
from backend.services.client_service import ClientService
from config.database import DatabaseManager


def _format_date(value):
    """Safely format a date or string into readable text."""
    if not value:
        return ""
    if isinstance(value, (datetime, date)):
        return value.strftime("%d %B %Y")
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).strftime("%d %B %Y")
        except Exception:
            return value
    return str(value)


def _deep_merge(base: dict, updates: dict):
    """Recursively merge updates into base (in-place)."""
    for k, v in (updates or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
    return base


class DocumentGenerationService:
    """DOCX document generation orchestration service"""

    def __init__(self):
        self.doc_service = DocumentService()
        self.template_service = TemplateService()
        self.client_service = ClientService()
        self.db = DatabaseManager()
        self.templates_json_dir = os.path.join("templates_json")

        self.template_json_filename_map = {
            "change_of_circumstance": "change_of_circumstances.json",
            "change_of_circumstances": "change_of_circumstances.json",
            "progress_report": "progress_report.json",
            "support_plan": "support_plan_assessment.json",
            "support_plan_assessment": "support_plan_assessment.json",
            "assessment": "assessment.json",
            "implementation_report": "implementation_report.json",
        }

    # ------------------ helpers ------------------
    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = "_") -> dict:
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, new_key, sep=sep))
            else:
                items[new_key] = v
        return items
    
    def _normalize_for_docxtpl(self, data):
        """
        Recursively normalize data for docxtpl:
        - Keep dicts intact
        - Convert lists -> safe comma-separated strings
        - Convert None -> ""
        """
        if isinstance(data, dict):
            return {k: self._normalize_for_docxtpl(v) for k, v in data.items()}
        elif isinstance(data, list):
            # If list of dicts, keep as-is (so {% for x in list %} works in template)
            if all(isinstance(i, dict) for i in data):
                return [self._normalize_for_docxtpl(i) for i in data]
            # Otherwise, flatten to string
            return ", ".join(str(self._normalize_for_docxtpl(v)) for v in data)
        elif data is None:
            return ""
        else:
            return data

    def _load_template_schema(self, template_type: str) -> Dict[str, Any]:
        filename = self.template_json_filename_map.get(template_type) or f"{template_type}.json"
        path = os.path.join(self.templates_json_dir, filename)

        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f) or {}
            except Exception:
                return {}
        fallback = os.path.join(self.templates_json_dir, f"{template_type}.json")
        if os.path.exists(fallback):
            try:
                with open(fallback, "r", encoding="utf-8") as f:
                    return json.load(f) or {}
            except Exception:
                return {}
        return {}

    def _get_latest_extracted(self, client_id: int, template_type: str) -> dict:
        query = """
            SELECT extracted_json, raw_json
            FROM client_extracted_data
            WHERE client_id = ? AND template_type = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        rows = self.db.execute_query(query, (client_id, template_type))
        if not rows:
            return {}

        row = rows[0]
        cand = None
        if "extracted_json" in row.keys() and row["extracted_json"]:
            cand = row["extracted_json"]
        elif "raw_json" in row.keys() and row["raw_json"]:
            cand = row["raw_json"]

        if not cand:
            return {}

        try:
            return json.loads(cand)
        except Exception as e:
            print(f"⚠️ Failed to parse extracted_json: {e}")
            return {}

    # ------------------ prepare context ------------------
    def _prepare_template_context(
        self, client, coordinator_data: Dict[str, Any], context: str, template_type: str
    ) -> Dict[str, Any]:
        flat_context = {
            "full_name": client.full_name,
            "ndis_number": client.ndis_number,
            "email": client.email or "",
            "phone": client.phone or "",
            "plan_start_date": _format_date(client.plan_start_date),
            "plan_end_date": _format_date(client.plan_end_date),
            "conditions": ", ".join(client.conditions) if getattr(client, "conditions", None) else "",
            "goals_other": client.goals_other or "",
            "coordinator_name": coordinator_data.get("coordinator_name", ""),
            "provider_name": coordinator_data.get("provider_name", ""),
            "coordinator_email": coordinator_data.get("email", ""),
            "coordinator_phone": coordinator_data.get("phone", ""),
            "context": context,
            "template_type": template_type,
            "generated_date": datetime.now().strftime("%d %B %Y"),
        }

        participant = {
            "name": client.full_name,
            "ndis_number": client.ndis_number,
            "email": client.email or "",
            "phone": client.phone or "",
            "plan_start_date": _format_date(client.plan_start_date),
            "plan_end_date": _format_date(client.plan_end_date),
            "conditions": client.conditions or [],
            "goals_other": client.goals_other or "",
        }

        provider_details = {
            "provider_name": coordinator_data.get("provider_name", ""),
            "person_completing": coordinator_data.get("coordinator_name", ""),
            "phone": coordinator_data.get("phone", ""),
            "email": coordinator_data.get("email", ""),
        }

        meta = {
            "context": context,
            "template_type": template_type,
            "generated_date": datetime.now().strftime("%d %B %Y"),
        }

        schema_defaults = self._load_template_schema(template_type)
        if not isinstance(schema_defaults, dict):
            schema_defaults = {}

        extracted = self._get_latest_extracted(client.id, template_type) or {}
        if isinstance(extracted, dict):
            _deep_merge(schema_defaults, extracted)

        context_data = {
            **flat_context,
            "participant": participant,
            "participant_details": participant,
            "client": participant,
            "client_details": participant,
            "provider_details": provider_details,
            "coordinator": {
                "coordinator_name": coordinator_data.get("coordinator_name", ""),
                "email": coordinator_data.get("email", ""),
                "phone": coordinator_data.get("phone", ""),
            },
            "meta": meta,
            "extracted": extracted or {},
        }

        for k, v in schema_defaults.items():
            if k not in context_data:
                context_data[k] = v

        if extracted and isinstance(extracted, dict) and "participant" in extracted and isinstance(extracted["participant"], dict):
            merged_participant = {**participant}
            if "participant" in schema_defaults and isinstance(schema_defaults["participant"], dict):
                merged_participant.update(schema_defaults["participant"])
            merged_participant.update(extracted["participant"])
            context_data["participant"] = merged_participant
            context_data["participant_details"] = merged_participant
            context_data["client"] = merged_participant
            context_data["client_details"] = merged_participant

        flattened_underscore = self._flatten_dict(context_data, sep="_")
        context_data.update(flattened_underscore)

        # ✅ Normalize everything so docxtpl sees only safe strings/scalars
        context_data = self._normalize_for_docxtpl(context_data)

        # Debug
        try:
            print("=== CONTEXT DATA BEING PASSED TO TEMPLATE ===")
            print(f"Template Type: {template_type}, Client ID: {client.id}")
            print("📥 RAW EXTRACTED (from DB):", extracted)
            print("📤 Final participant object:", context_data.get("participant"))
            print("=" * 50)
        except Exception:
            pass

        return context_data

    # ------------------ main generation ------------------
    def generate_docx_document(
        self, client_id: int, template_type: str,
        context: str, coordinator_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            client = self.client_service.get_client_by_id(client_id)
            if not client:
                raise ValueError(f"Client {client_id} not found")

            template = self.template_service.get_template_by_type(template_type)
            if not template:
                raise ValueError(f"Template type {template_type} not found")

            template_path = self.doc_service.get_template_path(template_type)
            context_data = self._prepare_template_context(client, coordinator_data, context, template_type)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = client.full_name.replace(" ", "_")
            output_filename = f"{template_type}_{safe_name}_{timestamp}"

            output_path = self.doc_service.generate_docx_from_template(
                template_path, context_data, output_filename
            )

            document_name = f"{template['name']} - {client.full_name}"
            content_json = {
                "context_data": context_data,
                "markdown_context": f"# {template['name']}\n\n{context}",
            }

            query = """
                INSERT INTO generated_documents
                (coordinator_id, client_id, template_id, template_type,
                document_name, content, output_path, version, credits_used, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            doc_id = self.db.execute_insert(query, (
                coordinator_data.get("id"),
                client.id,
                template["id"],
                template_type,
                document_name,
                json.dumps(content_json, indent=2),
                output_path,
                1,
                10,
                "draft"
            ))

            return {
                "document_id": doc_id,
                "document_name": document_name,
                "template_type": template_type,
                "client_name": client.full_name,
                "output_path": output_path,
                "context_data": context_data,
                "content": content_json["markdown_context"],
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise Exception(f"Document generation failed: {str(e)}")
