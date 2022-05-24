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

from app.config import ConfigClass
from tmp_common.common.project.project_client import ProjectClient

async def query_project(project_code: str) -> dict:
    project_client = ProjectClient(
        ConfigClass.PROJECT_SERVICE,
        ConfigClass.REDIS_DB_URI
    )
    project = await project_client.get(code=project_code)
    return project
