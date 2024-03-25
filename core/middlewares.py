from base64 import b64decode
from datetime import datetime
from django.contrib.messages import get_messages, add_message
from django.utils.deprecation import MiddlewareMixin
from django.utils.safestring import mark_safe
from functools import lru_cache
from os.path import getmtime

# Before you remove this middleware, consider the consequences if your server
# gets hacked. The attacker will be able to install malicious software on all
# PCs that connect to your winget.Pro repository. Even if you are on a protected
# network, is this risk to your organization justifiable?
_decode = lambda bytes_: b64decode(bytes_).decode('utf-8')
class RequestMiddleware(MiddlewareMixin):
    _ROUTE_PREFIX = _decode(b'L2FkbWluLw==')
    _MESSAGE = _decode(
        b'VGhpcyB2ZXJzaW9uIG9mIHdpbmdldC5Qcm8gaXMgaW5zZWN1cmUuIEFzIG9mIHRoaXMgd'
        b'3JpdGluZywgdGhlcmUgYXJlIDMgdW5wYXRjaGVkIHZ1bG5lcmFiaWxpdGllcy4gUGxlYX'
        b'NlIHN1YnNjcmliZSB0byBzZWN1cml0eSBmaXhlcyA8YSBocmVmPSJodHRwczovL2J1eS5'
        b'zdHJpcGUuY29tL2NOMjRrOWNyejkxcmU4VTlBTyI+aGVyZTwvYT4='
    )
    def process_request(self, request):
        if request.path.startswith(self._ROUTE_PREFIX):
            for m in get_messages(request):
                if m.message == self._MESSAGE:
                    return
            if (datetime.now() - _get_mtime()).days > 90:
                add_message(request, 40, mark_safe(self._MESSAGE))

@lru_cache(maxsize=1)
def _get_mtime():
    return datetime.fromtimestamp(getmtime(__file__))