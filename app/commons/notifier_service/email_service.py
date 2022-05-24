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
import httpx

from app.config import ConfigClass


class SrvEmail():
    async def send(self, subject, receiver, sender, content='', msg_type='plain', template=None, template_kwargs={}):
        url = ConfigClass.EMAIL_SERVICE
        payload = {
            'subject': subject,
            'sender': sender,
            'receiver': [receiver],
            'msg_type': msg_type,
        }
        if content:
            payload['message'] = content
        if template:
            payload['template'] = template
            payload['template_kwargs'] = template_kwargs
        async with httpx.AsyncClient() as client:
            res = await client.post(
                url=url,
                json=payload
            )
        return res.json()
