import os
import platform
from docx2pdf import convert

def docx_to_pdf_crossplatform(input_path: str, output_path: str = None) -> str:
    """
    Convert DOCX to PDF using docx2pdf.
    - On Windows: uses Microsoft Word (must be installed).
    - On Mac/Linux: requires LibreOffice (must be installed and in PATH).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"DOCX file not found: {input_path}")
    
    # Default output path
    if not output_path:
        base, _ = os.path.splitext(input_path)
        output_path = base + ".pdf"

    try:
        convert(input_path, output_path)
    except Exception as e:
        raise RuntimeError(f"PDF conversion failed: {str(e)}")

    if not os.path.exists(output_path):
        raise RuntimeError(f"PDF file not created: {output_path}")
    
    return os.path.abspath(output_path)
