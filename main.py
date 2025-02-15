from followthemoney import model
from ingestors.manager import Manager

manager = Manager()
entity = manager.make_entity("Document")
entity.id = "1"
path = "/host/Documents/doc_with_images.docx"
manager.ingest(path, entity)
print(manager.emitted)

