from sqlalchemy.orm import sessionmaker
from database import engine
from models import UploadedFile
import logging
from ingestors.manager import ingest_file
from schemas import Status

SessionLocal = sessionmaker(bind=engine)

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def process_metadata(row_id):
    session = SessionLocal()
    try:
        file_record = session.query(UploadedFile).filter_by(id=row_id).first()
        if file_record:
            ingested_data = ingest_file(file_record.file_location, file_record.language)
            file_record.file_metadata = {
                **ingested_data["file_metadata"]
            }
            file_record.status = ingested_data["status"]
            file_record.text = ingested_data["text"]

            logger.info(f"Successfully processed row {row_id}.")
        else:
            logger.warning(f"No record found with id {row_id}.")
    except Exception as e:
        file_record.status = Status.FAILED.value
        logger.error(f"Error processing row {row_id}: {e}", exc_info=True)
    finally:
        session.commit()
        session.close()
