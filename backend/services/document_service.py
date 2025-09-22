import os
from docxtpl import DocxTemplate


def _flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    Flatten nested dictionary so nested JSON keys work in {{a.b.c}} placeholders.
    Example:
        {"participant": {"name": "Ali"}} -> {"participant.name": "Ali"}
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(_flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


class DocumentService:
    """Service for handling DOCX template operations"""

    def __init__(self):
        self.base_output = os.path.join("output", "generated")
        os.makedirs(self.base_output, exist_ok=True)  # ✅ ensure folder exists

    def get_template_path(self, template_type: str) -> str:
        """Return template file path (maps DB template_type to file path)"""
        template_map = {
            "change_of_circumstance": os.path.join("templates", "docx_templates", "change_of_circumstances.docx"),
            "progress_report": os.path.join("templates", "docx_templates", "progress_report.docx"),
            "support_plan": os.path.join("templates", "docx_templates", "support_plan.docx"),
            "assessment": os.path.join("templates", "docx_templates", "assessment.docx"),
            "implementation_report": os.path.join("templates", "docx_templates", "implementation_report.docx"),
        }

        path = template_map.get(template_type)
        if not path or not os.path.exists(path):
            raise FileNotFoundError(f"Template file not found for type '{template_type}': {path}")

        return path

    def generate_docx_from_template(self, template_path: str, context_data: dict, filename: str) -> str:
        """Generate DOCX document from template and data"""
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")

        # ✅ Load template
        doc = DocxTemplate(template_path)

        # ✅ Flatten nested dict so {{participant_details.name}} works
        flat_context = _flatten_dict(context_data)

        # ✅ Merge original + flattened
        render_context = {**context_data, **flat_context}

        # ✅ Render placeholders
        doc.render(render_context)

        # ✅ Build output path (single .docx extension only)
        output_path = os.path.join(self.base_output, f"{filename}.docx")

        # ✅ Save the generated DOCX
        doc.save(output_path)

        return os.path.abspath(output_path)  # return absolute path for frontend
