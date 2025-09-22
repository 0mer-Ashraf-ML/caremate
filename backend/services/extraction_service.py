# backend/services/extraction_service.py
import os
import json
from datetime import datetime
import docx
import PyPDF2
from config.database import DatabaseManager
import google.generativeai as genai


class ExtractionService:
    """Handles raw text extraction + Gemini JSON filling + DB storage"""

    def __init__(self):
        self.db = DatabaseManager()
        self.templates_dir = "templates_json"

        # ✅ Configure Gemini Client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not set in environment")
        genai.configure(api_key=api_key)

    # ----------------- File Handling -----------------
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF, DOCX, or TXT"""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            text = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text() or "")
            return "\n".join(text)

        elif ext == ".docx":
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])

        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        else:
            raise ValueError(f"Unsupported file type: {ext}")

    # ----------------- Step 1: Store Raw Document -----------------
    def store_raw_document(self, client_id: int, template_type: str, file_path: str):
        """Extract text from uploaded file and store raw version in DB"""
        text = self._extract_text(file_path)

        query = """
            INSERT INTO client_extracted_data
            (client_id, template_type, raw_json, created_at)
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_insert(query, (
            client_id,
            template_type,
            text,
            datetime.now().isoformat()
        ))
        print(f"✅ Raw text stored for client {client_id}, template {template_type}")

    # ----------------- Step 2: Load Template Schema -----------------
    def _load_template_schema(self, template_type: str) -> dict:
        """Load JSON schema for a given template_type"""
        template_map = {
            "change_of_circumstance": "change_of_circumstances.json",
            "progress_report": "progress_report.json",
            "implementation_report": "implementation_report.json",
            "support_plan": "support_plan_assessment.json",
            "support_plan_assessment": "support_plan_assessment.json",
        }

        filename = template_map.get(template_type, f"{template_type}.json")
        schema_path = os.path.join(self.templates_dir, filename)

        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"No schema found for template: {template_type} → {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ----------------- Step 3: Gemini AI Call -----------------
    def _call_gemini(self, template_type: str, schema: dict, text: str) -> dict:
        """Call Gemini to fill JSON schema with extracted info"""
        prompt = f"""
        You are an assistant that extracts structured information for NDIS reports.

        Given the following input text (an uploaded document), 
        fill the provided JSON schema with the extracted details.

        - Only return valid JSON.
        - Do not invent extra fields not present in the schema.
        - If information is missing, leave the field empty or null.

        Schema:
        {json.dumps(schema, indent=2)}

        Document:
        {text[:4000]}  # limit prompt size
        """

        response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
        raw_text = response.text.strip()

        # Some responses may include ```json ... ```
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").replace("json", "", 1).strip()

        try:
            extracted_json = json.loads(raw_text)
        except Exception:
            extracted_json = schema  # fallback to empty schema

        return {
            "template_type": template_type,
            "extracted": extracted_json,
            "markdown_summary": f"### Extracted {template_type}\n```json\n{json.dumps(extracted_json, indent=2)}\n```"
        }

    # ----------------- Step 4: Process with Schema -----------------
    def process_with_schema(self, client_id: int, template_type: str) -> dict:
        """
        Take stored raw text → load schema → call Gemini → save structured JSON.
        Always reuses the latest raw text for the client, regardless of template_type.
        """
        # 1️⃣ Get latest raw text for this client (ignore template_type)
        query = """
            SELECT id, raw_json
            FROM client_extracted_data
            WHERE client_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        rows = self.db.execute_query(query, (client_id,))
        if not rows:
            raise ValueError(f"No raw text found for client {client_id}")

        row = rows[0]
        raw_text = row["raw_json"] if "raw_json" in row.keys() else row[1]

        # 2️⃣ Load schema
        schema = self._load_template_schema(template_type)

        # 3️⃣ Ask Gemini to extract structured info
        structured = self._call_gemini(template_type, schema, raw_text)

        # 4️⃣ Store extracted JSON as a new row (so you can keep multiple templates for one raw file)
        insert_query = """
            INSERT INTO client_extracted_data
            (client_id, template_type, raw_json, extracted_json, markdown_summary, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute_insert(insert_query, (
            client_id,
            template_type,
            raw_text,
            json.dumps(structured["extracted"], indent=2),
            structured["markdown_summary"],
            datetime.now().isoformat(),
            datetime.now().isoformat(),
        ))

        print(f"✅ Processed raw → structured for client {client_id}, template {template_type}")
        return structured
