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
import re
from uuid import uuid4

import pytest
from app.config import ConfigClass
from tests.conftest import DEST_FOLDER_ID, FILE_DATA, FOLDER_DATA, SRC_FOLDER_ID

TEST_ID_1 = str(uuid4())
TEST_ID_2 = str(uuid4())
TEST_ID_3 = str(uuid4())


@pytest.mark.dependency()
def test_create_request_200(
    test_client,
    httpx_mock,
    mock_project,
    mock_src,
    mock_dest,
    mock_user,
    mock_roles
):
    # entity_geids file
    FILE_DATA_1 = FILE_DATA.copy()
    FILE_DATA_1['id'] = TEST_ID_1
    FILE_DATA_1['parent'] = TEST_ID_2
    mock_data = {'result': [FILE_DATA_1, FOLDER_DATA]}
    url = re.compile('^' + ConfigClass.META_SERVICE + 'items/batch.*$')
    httpx_mock.add_response(
        method='GET',
        url=url,
        json=mock_data,
        status_code=200
    )

    # mock notification
    httpx_mock.add_response(
        method='POST',
        url=ConfigClass.EMAIL_SERVICE,
        json={}
    )

    # mock get file list
    mock_data = {
        'result': [FILE_DATA_1]
    }
    url = re.compile('^' + ConfigClass.META_SERVICE + 'items/search.*$')
    httpx_mock.add_response(
        method='GET',
        url=url,
        json=mock_data,
        status_code=200
    )

    payload = {
        'entity_ids': [TEST_ID_1, TEST_ID_2],
        'destination_id': DEST_FOLDER_ID,
        'source_id': SRC_FOLDER_ID,
        'note': 'testing',
        'submitted_by': 'admin',
    }
    response = test_client.post('/v1/request/copy/approval_fake_project', json=payload)
    assert response.status_code == 200
    assert response.json()['result']['destination_id'] == DEST_FOLDER_ID
    assert response.json()['result']['note'] == 'testing'


@pytest.mark.dependency(depends=['test_create_request_200'])
def test_list_requests_200(test_client):
    payload = {
        'status': 'pending'
    }
    response = test_client.get('/v1/request/copy/approval_fake_project', params=payload)
    assert response.status_code == 200
    assert response.json()['result'][0]['destination_id'] == DEST_FOLDER_ID
    assert response.json()['result'][0]['note'] == 'testing'


@pytest.mark.dependency(depends=['test_create_request_200'])
def test_list_request_files_200(test_client):
    payload = {
        'status': 'pending'
    }
    response = test_client.get('/v1/request/copy/approval_fake_project', params=payload)
    request_obj = response.json()['result'][0]

    payload = {
        'request_id': request_obj['id'],
        'order_by': 'name',
        'order_type': 'desc',
    }
    response = test_client.get('/v1/request/copy/approval_fake_project/files', params=payload)
    assert response.status_code == 200
    assert len(response.json()['result']['data']) == 2
    assert len(response.json()['result']['routing']) == 0
    assert response.json()['result']['data'][0]['name'] == 'test_folder'
    assert response.json()['result']['data'][1]['name'] == 'test_file'


@pytest.mark.dependency(depends=['test_create_request_200'])
def test_list_request_files_query_200(test_client):
    payload = {
        'status': 'pending',
    }
    response = test_client.get('/v1/request/copy/approval_fake_project', params=payload)
    request_obj = response.json()['result'][0]

    payload = {
        'request_id': request_obj['id'],
        'order_by': 'name',
        'order_type': 'desc',
        'query': '{"name": "test_file"}',
        'parent_id': TEST_ID_2,
    }
    response = test_client.get('/v1/request/copy/approval_fake_project/files', params=payload)
    assert response.status_code == 200
    assert len(response.json()['result']['data']) == 2
    assert len(response.json()['result']['routing']) == 0
    assert response.json()['result']['data'][0]['name'] == 'test_file'


@pytest.mark.dependency(depends=['test_create_request_200'])
def test_approve_partial_files_200(test_client, httpx_mock, mock_project):
    payload = {
        'status': 'pending'
    }
    response = test_client.get('/v1/request/copy/approval_fake_project', params=payload)
    request_obj = response.json()['result'][0]

    # mock trigger pipeline
    httpx_mock.add_response(
        method='POST',
        url=ConfigClass.DATA_UTILITY_SERVICE + 'files/actions/',
        json={'result': ''})

    payload = {
        'entity_ids': [
            TEST_ID_1
        ],
        'request_id': request_obj['id'],
        'review_status': 'approved',
        'username': 'admin',
        'session_id': 'admin-123'
    }
    headers = {
        'Authorization': 'fake',
        'Refresh-Token': 'fake',
    }
    response = test_client.patch('/v1/request/copy/approval_fake_project/files', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()['result']['updated'] == 3
    assert response.json()['result']['approved'] == 0
    assert response.json()['result']['denied'] == 0


@pytest.mark.dependency(depends=['test_create_request_200'])
def test_approve_all_files_200(test_client, httpx_mock, mock_project):
    payload = {
        'status': 'pending'
    }
    response = test_client.get('/v1/request/copy/approval_fake_project', params=payload)
    request_obj = response.json()['result'][0]

    # mock trigger pipeline
    httpx_mock.add_response(
        method='POST',
        url=ConfigClass.DATA_UTILITY_SERVICE + 'files/actions/',
        json={'result': ''})

    payload = {
        'request_id': request_obj['id'],
        'review_status': 'approved',
        'username': 'admin',
        'session_id': 'admin-123'
    }
    headers = {
        'Authorization': 'fake',
        'Refresh-Token': 'fake',
    }
    response = test_client.put('/v1/request/copy/approval_fake_project/files', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()['result']['updated'] == 0
    assert response.json()['result']['approved'] == 3
    assert response.json()['result']['denied'] == 0


@pytest.mark.dependency(depends=['test_create_request_200'])
def test_complete_request_200(test_client, httpx_mock, mock_user, mock_project):
    payload = {
        'status': 'pending'
    }
    response = test_client.get('/v1/request/copy/approval_fake_project', params=payload)
    request_obj = response.json()['result'][0]

    # mock notification
    httpx_mock.add_response(
        method='POST',
        url=ConfigClass.EMAIL_SERVICE,
        json={}
    )

    payload = {
        'request_id': request_obj['id'],
        'session_id': 'admin-123',
        'status': 'complete',
        'review_notes': 'done',
        'username': 'admin',
    }
    response = test_client.put('/v1/request/copy/approval_fake_project', json=payload)
    assert response.status_code == 200
    assert response.json()['result']['status'] == 'complete'
    assert response.json()['result']['pending_count'] == 0


def test_create_request_sub_file_200(
    test_client,
    httpx_mock,
    mock_project,
    mock_dest,
    mock_src,
    mock_user,
    mock_roles
):
    file_data = FILE_DATA.copy()
    file_data['id'] = str(uuid4())
    file_data['parent_path'] = ''

    # mock notification
    httpx_mock.add_response(
        method='POST',
        url=ConfigClass.EMAIL_SERVICE,
        json={}
    )

    mock_data = {'result': [file_data]}
    url = re.compile('^' + ConfigClass.META_SERVICE + 'items/batch.*$')
    httpx_mock.add_response(
        method='GET',
        url=url,
        json=mock_data,
        status_code=200
    )

    mock_data = {
        'result': [file_data]
    }
    url = re.compile('^' + ConfigClass.META_SERVICE + 'items/search.*$')
    httpx_mock.add_response(
        method='GET',
        url=url,
        json=mock_data,
        status_code=200
    )

    payload = {
        'entity_ids': [file_data['id']],
        'destination_id': DEST_FOLDER_ID,
        'source_id': SRC_FOLDER_ID,
        'note': 'testing',
        'submitted_by': 'admin',
    }
    response = test_client.post('/v1/request/copy/approval_fake_project', json=payload)
    assert response.status_code == 200
    assert response.json()['result']['destination_id'] == DEST_FOLDER_ID
    assert response.json()['result']['note'] == 'testing'


def test_deny_partial_files_200(test_client):
    payload = {
        'status': 'pending'
    }
    response = test_client.get('/v1/request/copy/approval_fake_project', params=payload)
    request_obj = response.json()['result'][0]

    payload = {
        'entity_ids': [
            FILE_DATA['id'],
        ],
        'request_id': request_obj['id'],
        'review_status': 'denied',
        'username': 'admin',
        'session_id': 'admin-123'
    }
    headers = {
        'Authorization': 'fake',
        'Refresh-Token': 'fake',
    }
    response = test_client.patch('/v1/request/copy/approval_fake_project/files', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()['result']['updated'] == 0
    assert response.json()['result']['approved'] == 0
    assert response.json()['result']['denied'] == 0


def test_partial_approved_200(
    test_client,
    httpx_mock,
    mock_dest,
    mock_src,
    mock_user,
    mock_project,
    mock_roles
):
    FILE_DATA_2 = FILE_DATA.copy()
    FILE_DATA_2['id'] = TEST_ID_3

    mock_data = {
        'result': [FILE_DATA_2]
    }
    url = re.compile('^' + ConfigClass.META_SERVICE + 'items/search.*$')
    httpx_mock.add_response(
        method='GET',
        url=url,
        json=mock_data,
        status_code=200
    )

    # mock trigger pipeline
    httpx_mock.add_response(
        method='POST',
        url=ConfigClass.DATA_UTILITY_SERVICE + 'files/actions/',
        json={'result': ''})

    # entity_geids file
    mock_data = {'result': [FILE_DATA_2]}
    url = re.compile('^' + ConfigClass.META_SERVICE + 'items/batch.*$')
    httpx_mock.add_response(
        method='GET',
        url=url,
        json=mock_data,
        status_code=200
    )

    # mock notification
    httpx_mock.add_response(
        method='POST',
        url=ConfigClass.EMAIL_SERVICE,
        json={}
    )

    payload = {
        'entity_ids': [FILE_DATA['id'], FILE_DATA_2['id']],
        'destination_id': DEST_FOLDER_ID,
        'source_id': SRC_FOLDER_ID,
        'note': 'testing',
        'submitted_by': 'admin',
    }
    response = test_client.post('/v1/request/copy/approval_fake_project', json=payload)
    assert response.status_code == 200
    assert response.json()['result']['destination_id'] == DEST_FOLDER_ID
    assert response.json()['result']['note'] == 'testing'

    request_obj = response.json()['result']

    payload = {
        'entity_ids': [
            FILE_DATA['id']
        ],
        'request_id': request_obj['id'],
        'review_status': 'denied',
        'username': 'admin',
        'session_id': 'admin-123'
    }
    headers = {
        'Authorization': 'fake',
        'Refresh-Token': 'fake',
    }
    response = test_client.patch('/v1/request/copy/approval_fake_project/files', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()['result']['updated'] == 0
    assert response.json()['result']['approved'] == 0
    assert response.json()['result']['denied'] == 0

    payload = {
        'entity_ids': [
            FILE_DATA_2['id']
        ],
        'request_id': request_obj['id'],
        'review_status': 'approved',
        'username': 'admin',
        'session_id': 'admin-123'
    }
    headers = {
        'Authorization': 'fake',
        'Refresh-Token': 'fake',
    }
    response = test_client.patch('/v1/request/copy/approval_fake_project/files', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()['result']['updated'] == 2
    assert response.json()['result']['approved'] == 0
    assert response.json()['result']['denied'] == 0


def test_complete_pending_400(
    test_client,
    httpx_mock,
    mock_dest,
    mock_src,
    mock_user,
    mock_project,
    mock_roles
):
    FILE_DATA_2 = FILE_DATA.copy()
    FILE_DATA_2['id'] = TEST_ID_3

    # entity_geids file
    mock_data = {'result': [FILE_DATA_2]}
    url = re.compile('^' + ConfigClass.META_SERVICE + 'items/batch.*$')
    httpx_mock.add_response(
        method='GET',
        url=url,
        json=mock_data,
        status_code=200
    )

    # mock notification
    httpx_mock.add_response(
        method='POST',
        url=ConfigClass.EMAIL_SERVICE,
        json={}
    )

    # mock get file list
    mock_data = {
        'result': [FILE_DATA_2]
    }
    url = re.compile('^' + ConfigClass.META_SERVICE + 'items/search.*$')
    httpx_mock.add_response(
        method='GET',
        url=url,
        json=mock_data,
        status_code=200
    )

    payload = {
        'entity_ids': [FILE_DATA_2['id']],
        'destination_id': DEST_FOLDER_ID,
        'source_id': SRC_FOLDER_ID,
        'note': 'testing',
        'submitted_by': 'admin',
    }
    response = test_client.post('/v1/request/copy/approval_fake_project', json=payload)
    assert response.status_code == 200
    assert response.json()['result']['destination_id'] == DEST_FOLDER_ID
    assert response.json()['result']['note'] == 'testing'

    request_obj = response.json()['result']

    payload = {
        'request_id': request_obj['id'],
        'session_id': 'admin-123',
        'status': 'complete',
        'review_notes': 'done',
        'username': 'admin',
    }
    response = test_client.put('/v1/request/copy/approval_fake_project', json=payload)
    assert response.status_code == 400
    assert response.json()['result']['status'] == 'pending'
    assert response.json()['result']['pending_count'] == 2


def test_pending_files_list_200(test_client, httpx_mock):
    # entity_geids file
    mock_data = {'result': [FILE_DATA]}
    url = re.compile('^' + ConfigClass.META_SERVICE + 'items/batch.*$')
    httpx_mock.add_response(
        method='GET',
        url=url,
        json=mock_data,
        status_code=200
    )

    payload = {
        'status': 'pending'
    }
    response = test_client.get('/v1/request/copy/approval_fake_project', params=payload)
    request_obj = response.json()['result'][0]

    payload = {
        'request_id': request_obj['id'],
    }
    response = test_client.get('/v1/request/copy/approval_fake_project/pending-files', params=payload)

    assert response.status_code == 200
    assert response.json()['result']['pending_entities'] == [TEST_ID_3, TEST_ID_3]
    assert response.json()['result']['pending_count'] == 2
