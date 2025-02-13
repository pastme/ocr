from followthemoney import model
from ingestors.manager import Manager

manager = Manager()
entity = manager.make_entity("Document")
path = "/host/Documents/doc_with_images.docx"
manager.ingest(path, entity)
emitted_entities = list(manager.emitted)
import pdb;pdb.set_trace()
print(emitted_entities)

