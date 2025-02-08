from ingestors.image import ImageIngestor
from followthemoney import model
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

image_ingestor = ImageIngestor(None)
schema = model.get("Image")
file_path = "/Users/petrodatsiuk/projects/vol/ocr/test_ingest.png"
entity = model.make_entity(schema)
image_ingestor.ingest(file_path, entity)
