import os
import json
import asyncio
import ctypes
import subprocess

TIMEOUT = 2.0
API_ID = os.environ.get('TDINBOX_API_ID')
API_HASH = os.environ.get('TDINBOX_API_HASH')
PHONE_NUMBER = os.environ.get('TDINBOX_PHONE_NUMBER')
PASSWORD = os.environ.get('TDINBOX_PASSWORD')
DB_ENCRYPTION_KEY = os.environ.get('TDINBOX_DB_ENCRYPTION_KEY')


pwd = os.path.dirname(os.path.realpath(__file__))
tdlib_path = os.path.join(pwd, 'libtdjson.so')
tdlib = ctypes.CDLL(tdlib_path)
_td_create = tdlib.td_json_client_create
_td_receive = tdlib.td_json_client_receive
_td_receive.restype = ctypes.c_char_p
_td_receive.argtypes = [ctypes.c_void_p, ctypes.c_double]
_td_send = tdlib.td_json_client_send
_td_send.restype = None
_td_send.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
_td_execute = tdlib.td_json_client_execute
_td_execute.restype = ctypes.c_char_p
_td_execute.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
_td_destroy = tdlib.td_json_client_destroy

_td_set_log_fatal_error_callback = tdlib.td_set_log_fatal_error_callback

client = _td_create()
loop = asyncio.get_event_loop()


class AuthenticationCode:

    @classmethod
    def __str__(cls) -> str:
        input('Please enter the authentication code you received: ')


def wrap_authorizationStateWaitCode(data):
    return {
        '@type': 'checkAuthenticationCode',
        'code': input("Login code: ")
    }


def wrap_authorizationStateWaitPassword(data):
    return {
        '@type': 'checkAuthenticationPassword',
        'password': PASSWORD
    }


def wrap_authorizationStateWaitPhoneNumber(data):
    return {
        '@type': 'setAuthenticationPhoneNumber',
        'phone_number': PHONE_NUMBER
    }


def wrap_ok(data):
    return {"@type": "getAuthorizationState"}


def wrap_authorizationStateWaitEncryptionKey(data):
    return {
        "@type": "checkDatabaseEncryptionKey",
        "encryption_key": DB_ENCRYPTION_KEY,
    }


def wrap_authorizationStateWaitTdlibParameters(data):
    return {
        "@type": "setTdlibParameters",
        "parameters": {
            "use_test_dc": False,
            "api_id": API_ID,
            "api_hash": API_HASH,
            "device_model": "Desktop",
            "system_version": "Unknown",
            "application_version": "0.0",
            "system_language_code": "en",
            "database_directory": os.path.join(pwd, 'data'),
            "files_directory": os.path.join(pwd, 'files'),
            "use_file_database": True,
            "use_chat_info_database": True,
            "use_message_database": True,
            "enable_storage_optimizer": False,
            "ignore_file_names": True,
        },
    }


def wrap_updateNewMessage(data):
    message = data.get('message')
    if not message:
        return
    sender_id = message.get('sender', {}).get('user_id')
    chat_id = message.get('chat_id')
    if sender_id == chat_id:
        rec = message
        content = message.get('content', {})
        if content['@type'] == 'messageText':
            rec = content['text']['text']
            try:
                commit_message(rec)
            except Exception as err:
                print("Error: {}".format(err))


def commit_message(msg):
    print("New message: {0}".format(msg))
    with open('/git/Inbox.md', 'a') as inbox:
        inbox.write(msg + '\n\n')
    subprocess.check_call(["git", "add", "Inbox.md"], cwd='/git')
    subprocess.check_call(["git", "commit", "-m", "tdinbox"], cwd='/git')


def td_receive(client):
    return json.loads((_td_receive(client, TIMEOUT) or b'{"@type": "empty"}').decode('utf-8'))


def td_send(command):
    command and loop.create_task(send(command))


def td_execute(client, command):
    return json.loads((_td_execute(client, json.dumps(command).encode("utf-8")) or b'{"@type": "empty"}').decode('utf-8'))


async def main_loop():
    while True:
        await asyncio.sleep(0)
        event = td_receive(client)
        wrap = globals().get("wrap_" + event.pop('@type'))
        if wrap:
            res = wrap(event)
            if res:
                td_send(res)


async def send(command):
    _td_send(client, json.dumps(command).encode('utf-8'))


loop.create_task(main_loop())
td_execute(client, { "@type": "setLogVerbosityLevel", "new_verbosity_level": 1, "@extra": 1.01234, })
td_send({"@type": "getAuthorizationState"})

try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
    _td_destroy(client)
