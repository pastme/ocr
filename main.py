from ingestors.pdf import PDFIngestor
from followthemoney import model
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

pdf_ingestor = PDFIngestor(None)
schema = model.get("Document")
file_path = "/Users/petrodatsiuk/projects/vol/ocr/pdf_with_images.pdf"
entity = model.make_entity(schema)
pdf_ingestor.ingest(file_path, entity)
