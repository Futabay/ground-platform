from sqlalchemy import text
from app.db.base import Base
from app.db.session import engine


def init_db():
    # Create plain table via SQLAlchemy metadata
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        # Enable Timescale extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))

        # Convert telemetry table to hypertable and migrate existing data
        # - if_not_exists => TRUE: don't error if it's already a hypertable
        # - migrate_data => TRUE: move existing rows into the hypertable
        conn.execute(
            text(
                "SELECT create_hypertable("
                "  'telemetry', "
                "  'timestamp', "
                "  if_not_exists => TRUE, "
                "  migrate_data => TRUE"
                ");"
            )
        )

        conn.commit()


if __name__ == "__main__":
    init_db()
