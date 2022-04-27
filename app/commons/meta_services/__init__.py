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
from typing import List

import httpx

from app.config import ConfigClass
from app.models.base import EAPIResponseCode
from app.resources.error_handler import APIException


def get_node_by_id(entity_id: str) -> dict:
    response = httpx.get(ConfigClass.META_SERVICE + f'item/{entity_id}')
    if response.status_code != 200:
        error_msg = f'Error calling Meta service get_node_by_id: {response.json()}'
        raise APIException(error_msg=error_msg, status_code=EAPIResponseCode.internal_error.value)
    if not response.json()['result']:
        error_msg = 'Folder not found'
        raise APIException(error_msg=error_msg, status_code=EAPIResponseCode.not_found.value)
    return response.json()['result']


def bulk_get_by_ids(ids: List[str]) -> List[dict]:
    query_data = {'ids': ids}
    response = httpx.get(ConfigClass.META_SERVICE + 'items/batch', params=query_data)
    if response.status_code != 200:
        error_msg = f'Error calling Meta service bulk_get_by_ids: {response.json()}'
        raise APIException(error_msg=error_msg, status_code=EAPIResponseCode.internal_error.value)
    return response.json()['result']


def get_files_recursive(entity: dict) -> list:
    parent_path = entity['parent_path']
    name = entity['name']
    query_data = {
        'container_code': entity['container_code'],
        'zone': entity['zone'],
        'recursive': True,
        'parent_path': f'{parent_path}.{name}'
    }
    response = httpx.get(ConfigClass.META_SERVICE + 'items/search', params=query_data)
    if response.status_code != 200:
        error_msg = f'Error calling Meta service get_files_recursive: {response.json()}'
        raise APIException(error_msg=error_msg, status_code=EAPIResponseCode.internal_error.value)
    return response.json()['result']
