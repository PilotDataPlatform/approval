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
from app.config import ConfigClass
from app.models.base import EAPIResponseCode
from app.resources.error_handler import APIException


def query_node(label: str, query_data: dict) -> dict:
    response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/{label}/query", json=query_data)
    if response.status_code != 200:
        error_msg = f"Error calling Neo4j service: {response.json()}"
        raise APIException(error_msg=error_msg, status_code=EAPIResponseCode.internal_error.value)
    if not response.json():
        error_msg = f"{label} not found: {query_data}"
        raise APIException(error_msg=error_msg, status_code=EAPIResponseCode.not_found.value)
    return response.json()[0]
