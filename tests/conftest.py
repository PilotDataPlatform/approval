# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import pytest
import requests_mock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateSchema, CreateTable
from sqlalchemy_utils import create_database, database_exists
from testcontainers.postgres import PostgresContainer

from app.config import ConfigClass
from app.main import create_app
from app.models.copy_request_sql import Base, EntityModel, RequestModel

FILE_DATA = {
    "global_entity_id": "approval_test_geid1",
    "labels": ["File", "Greenroom"],
    "display_path": "test/",
    "name": "test_file",
    "time_created": "2021-06-09T13:44:12.381872077",
    "uploader": "admin",
    "file_size": 123,
    "parent_folder_geid": "approval_test_geid2",
    "archived": False,
}

FOLDER_DATA = {
    "global_entity_id": "approval_test_geid2",
    "labels": ["Folder", "Greenroom"],
    "display_path": "test/",
    "name": "test_folder",
    "time_created": "2021-06-09T13:44:12.381872077",
    "uploader": "admin",
    "archived": False,
}

USER_DATA = {
    "first_name": "Greg",
    "last_name": "Testing",
    "username": "greg",
    "email": "greg@test.com",
}


@pytest.fixture(scope='function')
def requests_mocker(request):
    kw = {'real_http': True}
    with requests_mock.Mocker(**kw) as m:
        yield m


@pytest.fixture
def mock_project(requests_mocker):
    # mock get project
    mock_data = [{
        "code": "testing",
        "name": "Testing",
    }]
    requests_mocker.post(ConfigClass.NEO4J_SERVICE + "nodes/Container/query", json=mock_data)


@pytest.fixture
def mock_user(requests_mocker):
    # mock get user
    user_data = {"result":USER_DATA}
    requests_mocker.get(ConfigClass.AUTH_SERVICE + "admin/user", json=user_data)

@pytest.fixture
def mock_roles(requests_mocker):
    result = {
        "result": [{
            "email": "fake@fake.com",
            "username": "fake",
            "first_name": "fake",
        }],
    }
    requests_mocker.post(ConfigClass.AUTH_SERVICE + "admin/roles/users", json=result)


@pytest.fixture
def mock_src_dest_folder(requests_mocker):
    get_by_geid_url = ConfigClass.NEO4J_SERVICE + "nodes/geid/"
    mock_folder = FOLDER_DATA.copy()
    mock_folder["global_entity_id"] = "src_folder_geid"
    mock_data = [mock_folder]
    requests_mocker.get(get_by_geid_url + "src_folder_geid", json=mock_data)

    mock_folder = FOLDER_DATA.copy()
    mock_folder["global_entity_id"] = "dest_folder_geid"
    mock_data = [mock_folder]
    requests_mocker.get(get_by_geid_url + "dest_folder_geid", json=mock_data)

@pytest.fixture(scope='session', autouse=True)
def db():
    with PostgresContainer("postgres:9.5") as postgres:
        postgres_uri  = postgres.get_connection_url()
        if not database_exists(postgres_uri):
            create_database(postgres_uri)
        engine = create_engine(postgres_uri)
        CreateTable(RequestModel.__table__).compile(dialect=postgresql.dialect())
        CreateTable(EntityModel.__table__).compile(dialect=postgresql.dialect())
        if not engine.dialect.has_schema(engine, ConfigClass.RDS_SCHEMA_DEFAULT):
            engine.execute(CreateSchema(ConfigClass.RDS_SCHEMA_DEFAULT))
        Base.metadata.create_all(bind=engine)
        yield postgres

@pytest.fixture
def test_client(db):
    ConfigClass.RDS_DB_URI = db.get_connection_url()
    app = create_app()
    client = TestClient(app)
    return client
