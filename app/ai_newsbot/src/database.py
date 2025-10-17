
import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Define the base for declarative models
Base = declarative_base()

class Source(Base):
    __tablename__ = 'sources'

    id = Column(String, primary_key=True)  # Using URL or a unique identifier as ID
    url = Column(String, unique=True, nullable=False)
    source_type = Column(String, nullable=False)  # e.g., 'website', 'document', 'repository'
    monitoring_frequency_seconds = Column(String, default=3600) # How often to check
    last_checked = Column(DateTime, default=datetime.now)
    last_hash = Column(String)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Source(url='{self.url}', type='{self.source_type}')>"

class GeneratedPost(Base):
    __tablename__ = 'generated_posts'

    id = Column(String, primary_key=True) # Unique ID for the post
    source_id = Column(String, nullable=False) # Foreign key to Source
    platform = Column(String, nullable=False)  # e.g., 'linkedin', 'instagram', 'twitter'
    content = Column(Text, nullable=False)
    metadata_json = Column(Text) # Store additional metadata as JSON string
    generated_at = Column(DateTime, default=datetime.now)
    status = Column(String, default='pending_review') # e.g., 'pending_review', 'approved', 'published'

    def __repr__(self):
        return f"<GeneratedPost(platform='{self.platform}', status='{self.status}')>"

def init_db(db_path='aladdin-sandbox/apps/ai_newsbot/data/newsbot.db'):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session

if __name__ == '__main__':
    # Example usage: Initialize the database and add a sample source
    Session = init_db()
    session = Session()

    # Add a sample source if it doesn't exist
    sample_url = "https://homecouver.com"
    if not session.query(Source).filter_by(url=sample_url).first():
        sample_source = Source(
            id="homecouver_website",
            url=sample_url,
            source_type="website",
            monitoring_frequency_seconds=3600
        )
        session.add(sample_source)
        session.commit()
        print(f"Added sample source: {sample_source.url}")
    else:
        print(f"Sample source already exists: {sample_url}")

    session.close()

