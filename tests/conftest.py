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
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateSchema, CreateTable
from sqlalchemy_utils import create_database, database_exists
from testcontainers.postgres import PostgresContainer

from app.config import ConfigClass
from app.main import create_app
from app.models.copy_request_sql import Base, EntityModel, RequestModel

DEST_FOLDER_ID = str(uuid4())
SRC_FOLDER_ID = str(uuid4())

FILE_DATA = {
    'id': str(uuid4()),
    'labels': ['File', 'Greenroom'],
    'display_path': 'test/',
    'name': 'test_file',
    'created_time': '2021-06-09T13:44:12.381872077',
    'owner': 'admin',
    'size': 123,
    'archived': False,
    'parent_path': 'fake.path',
    'container_code': 'testproject',
    'zone': 'Greenroom',
    'type': 'file',
    'parent': None,
}

FOLDER_DATA = {
    'id': str(uuid4()),
    'labels': ['Folder', 'Greenroom'],
    'display_path': 'test/',
    'name': 'test_folder',
    'created_time': '2021-06-09T13:44:12.381872077',
    'owner': 'admin',
    'archived': False,
    'parent_path': 'fake.path',
    'container_code': 'testproject',
    'zone': 'Greenroom',
    'type': 'folder',
    'parent': None,
}

USER_DATA = {
    'first_name': 'Greg',
    'last_name': 'Testing',
    'username': 'greg',
    'email': 'greg@test.com',
}


class TestProject:
    id = 1234
    labels = ['Container']
    global_entity_id = 'test-project-id'
    code = 'testproject'
    roles = ['admin', 'collaborator', 'contributor']
    type = 'Usecase'
    tags = ['tag1', 'tag2', 'tag3']
    path = 'testproject'
    time_lastmodified = '2022-04-06T20:25:07'
    discoverable = True
    system_tags = ['copied-to-core']
    name = 'Fake Test Project'
    time_created = '2021-05-07T16:14:18'


@pytest.fixture
def mock_project(mocker):
    # mock get project
    mocker.patch('common.project.project_client.ProjectClient.get', return_value=TestProject)


@pytest.fixture
def mock_user(httpx_mock: HTTPXMock):
    # mock get user
    user_data = {'result': USER_DATA}
    httpx_mock.add_response(
        method='GET', url=ConfigClass.AUTH_SERVICE + 'admin/user?username=admin&exact=true', json=user_data
    )


@pytest.fixture
def mock_roles(httpx_mock: HTTPXMock):
    result = {
        'result': [
            {
                'email': 'fake@fake.com',
                'username': 'fake',
                'first_name': 'fake',
            }
        ],
    }
    httpx_mock.add_response(method='POST', url=ConfigClass.AUTH_SERVICE + 'admin/roles/users', json=result)


@pytest.fixture
def mock_src(httpx_mock):
    get_by_geid_url = ConfigClass.META_SERVICE + 'item'
    mock_folder = FOLDER_DATA.copy()
    mock_folder['id'] = str(SRC_FOLDER_ID)
    mock_folder['name'] = 'src_folder'
    mock_data = {'result': mock_folder}
    httpx_mock.add_response(
        method='GET', url=get_by_geid_url + '/' + str(SRC_FOLDER_ID) + '/', json=mock_data, status_code=200
    )


@pytest.fixture
def mock_dest(httpx_mock):
    get_by_geid_url = ConfigClass.META_SERVICE + 'item'
    mock_folder = FOLDER_DATA.copy()
    mock_folder['id'] = str(DEST_FOLDER_ID)
    mock_folder['name'] = 'dest_folder'
    mock_data = {'result': mock_folder}
    httpx_mock.add_response(
        method='GET', url=get_by_geid_url + '/' + str(DEST_FOLDER_ID) + '/', json=mock_data, status_code=200
    )


@pytest.fixture(scope='session', autouse=True)
def db():
    with PostgresContainer('postgres:9.5') as postgres:
        postgres_uri = postgres.get_connection_url()
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
    ConfigClass.DB_URI = db.get_connection_url()
    app = create_app()
    client = TestClient(app)
    return client
