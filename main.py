from ingestors.manager import Manager

manager = Manager(context={"languages": ["ru"]})
entity = manager.make_entity("Document")
entity.id = "1"
path = "/host/Documents/test_ingest.png"
manager.ingest(path, entity)
print(manager.emitted)

