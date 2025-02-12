from ingestors.opendoc import OpenDocumentIngestor
from followthemoney import model

doc_ingestor = OpenDocumentIngestor(None)
schema = model.get("Document")
file_path = "/ingestors/test_files/doc_with_images.docx"
entity = model.make_entity(schema)
doc_ingestor.ingest(file_path, entity)
