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
import requests

from common import LoggerFactory
from app.config import ConfigClass
from app.models.base import EAPIResponseCode
from app.resources.error_handler import APIException

logger = LoggerFactory('api_copy_request').get_logger()


def trigger_copy_pipeline(
    request_id: str,
    project_geid: str,
    source_geid: str,
    destination_geid: str,
    entity_geids: list[str],
    username: str,
    session_id: str,
    auth: dict,
) -> dict:
    copy_data = {
        'payload': {
            'targets': [{'geid': i} for i in entity_geids],
            'destination': destination_geid,
            'source': source_geid,
            'request_id': request_id,
        },
        'operator': username,
        'operation': 'copy',
        'project_geid': project_geid,
        'session_id': session_id,
    }
    response = requests.post(ConfigClass.DATA_UTILITY_SERVICE + 'files/actions', json=copy_data, headers=auth)
    if response.status_code >= 300:
        error_msg = f'Failed to start copy pipeline: {response.content}'
        logger.error(error_msg)
        raise APIException(error_msg=error_msg, status_code=EAPIResponseCode.internal_error.value)
    return response.json()['result']
