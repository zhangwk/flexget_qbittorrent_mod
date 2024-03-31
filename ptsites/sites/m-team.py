from __future__ import annotations

import json
from typing import Final
from urllib.parse import urljoin

from requests import Response

from ..base.entry import SignInEntry
from ..base.reseed import ReseedPasskey
from ..base.sign_in import check_final_state, SignState, Work
from ..schema.nexusphp import NexusPHP
from ..utils.net_utils import get_module_name
from ..utils.value_handler import handle_infinite


class MainClass(NexusPHP, ReseedPasskey):
    URL: Final = 'https://kp.m-team.cc/'
    PROFILE_URL = '/api/member/profile'
    MY_PEER_STATUS = '/api/tracker/myPeerStatus'
    SUCCEED_REGEX = 'SUCCESS'
    USER_CLASSES: Final = {
        'downloaded': [2147483648000, 3221225472000],
        'share_ratio': [7, 9],
        'days': [168, 224]
    }

    @classmethod
    def sign_in_build_schema(cls) -> dict:
        return {
            get_module_name(cls): {
                'type': 'object',
                'properties': {
                    'key': {'type': 'string'}
                },
                'additionalProperties': False
            }
        }

    def get_details(self, entry: SignInEntry, config: dict) -> None:
        details_response_json = json.loads(entry['base_content'])
        if not details_response_json:
            return
        my_peer_status_response = self.request(entry, 'POST', urljoin(self.URL, self.MY_PEER_STATUS))
        my_peer_status_response_json = my_peer_status_response.json()
        entry['details'] = {
            'uploaded': f'{details_response_json.get("data").get("memberCount").get("uploaded") or 0} B'.replace(',',
                                                                                                                 ''),
            'downloaded': f'{details_response_json.get("data").get("memberCount").get("downloaded") or 0} B'.replace(
                ',',
                ''),
            'share_ratio': handle_infinite(
                str(details_response_json.get('data').get('memberCount').get('shareRate') or 0).replace(',', '')),
            'points': str(details_response_json.get('data').get('memberCount').get('bonus') or 0).replace(
                ',', ''),
            'seeding': str(my_peer_status_response_json.get('data').get('seeder') or 0).replace(',', ''),
            'leeching': str(my_peer_status_response_json.get('data').get('leecher') or 0).replace(',',
                                                                                                  '')
        }

    def sign_in_build_workflow(self, entry: SignInEntry, config: dict) -> list[Work]:
        return [
            Work(
                url=self.PROFILE_URL,
                method=self.sign_in_by_post,
                data={},
                succeed_regex=[self.SUCCEED_REGEX],
                assert_state=(check_final_state, SignState.SUCCEED),
                is_base_content=True
            )
        ]

    def request(self,
                entry: SignInEntry,
                method: str,
                url: str,
                **kwargs,
                ) -> Response | None:
        key = entry.get('site_config').get('key')
        return super().request(entry, 'POST', url, headers={'x-api-key': key})

    def get_messages(self, entry: SignInEntry, config: dict) -> None:
        return
