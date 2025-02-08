from ingestors.pdf import PDFIngestor
from followthemoney import model
import os

pdf_ingestor = PDFIngestor(None)
schema = model.get("Document")
file_path = "/host/Documents/pdf_with_images.pdf"
entity = model.make_entity(schema)
pdf_ingestor.ingest(file_path, entity)
