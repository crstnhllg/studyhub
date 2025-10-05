from app.models import User, StudyGroup, Membership, StudySession, Subject
from app.core.security import bcrypt_context, get_current_user
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime
import pytest
import os
from dotenv import load_dotenv

load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv('TEST_DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
client = TestClient(app)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope='function')
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    user = User(
        email='test@email.com',
        username='test',
        hashed_password=bcrypt_context.hash('12345')
        )

    db_session.add(user)
    db_session.commit()
    yield user


@pytest.fixture
def test_group(db_session, test_user):
    group = StudyGroup(
        name='Test Group',
        description='Test description.',
        owner_id=test_user.id
    )
    db_session.add(group)
    db_session.flush()

    owner = Membership(
        user_id=test_user.id,
        group_id=group.id,
        role='Creator'
    )
    db_session.add(owner)
    db_session.commit()
    yield group


@pytest.fixture()
def test_member(db_session, test_group):
    member = User(
        email='new_member@email.com',
        username='new_member',
        hashed_password='12345'
    )
    db_session.add(member)
    db_session.flush()

    membership = Membership(
        user_id=member.id,
        group_id=test_group.id,
        role='Member'
    )
    db_session.add(membership)
    db_session.commit()
    yield member


@pytest.fixture
def test_subject(db_session, test_group):
    subject = Subject(
        name='Test Subject',
        group_id=test_group.id
    )
    db_session.add(subject)
    db_session.commit()
    yield subject


@pytest.fixture
def test_session(db_session, test_subject, test_user):
    session = StudySession(
        title='Test Session',
        description='Test session description',
        date_time='2025-12-12 10:00',
        duration=60,
        status='Scheduled',
        subject_id=test_subject.id,
        created_by=test_user.id
    )
    db_session.add(session)
    db_session.commit()
    yield session


@pytest.fixture(autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def override_current_user(test_user):
    app.dependency_overrides[get_current_user] = lambda: test_user
