import typing as t
import sys
import os.path
import httplib2
from oauth2client import file, client
from oauth2client import tools
from oauth2client.clientsecrets import InvalidClientSecretsError
from oauth2client.client import OAuth2Credentials
from dictknife.langhelpers import reify
import googleapiclient.discovery

from logging import getLogger

logger = getLogger(__name__)

DEFAULT_CREDENTIALS_PATH = "~/.config/dictknife/credentials.json"

# Authorize using one of the following scopes:
#     'https://www.googleapis.com/auth/drive'
#     'https://www.googleapis.com/auth/drive.file'
#     'https://www.googleapis.com/auth/drive.readonly'
#     'https://www.googleapis.com/auth/spreadsheets'
#     'https://www.googleapis.com/auth/spreadsheets.readonly'
SCOPE = 'https://www.googleapis.com/auth/spreadsheets'
SCOPE_READONLY = 'https://www.googleapis.com/auth/spreadsheets.readonly'


def get_credentials(
    config_path: str,
    *,
    cache_path: t.Optional[str] = None,
    scopes: t.Sequence[str],
    logger: t.Any = logger,
) -> OAuth2Credentials:
    config_path = os.path.expanduser(config_path)
    if cache_path is None:
        cache_path = os.path.join(os.path.dirname(config_path), "token.json")

    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    logger.debug("see: %s", cache_path)
    store = file.Storage(cache_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        logger.info("credentials are invalid (or not found). %s", cache_path)
        logger.debug("see: %s", config_path)
        flow = client.flow_from_clientsecrets(config_path, scopes)
        flags = tools.argparser.parse_args(["--logging_level=DEBUG", "--noauth_local_webserver"])
        credentials = tools.run_flow(flow, store, flags=flags)
    return credentials


def get_credentials_failback_webbrowser(
    config_path: str,
    *,
    cache_path: t.Optional[str] = None,
    scopes: t.Optional[t.Sequence[str]] = None,
    logger: t.Any = logger,
) -> OAuth2Credentials:
    if scopes is None:
        import webbrowser
        url = "https://developers.google.com/identity/protocols/googlescopes"
        print(
            "please passing scopes: (e.g. 'https://www.googleapis.com/auth/spreadsheets.readonly')\nopening {}...".
            format(url),
            file=sys.stderr
        )
        webbrowser.open(url, new=1, autoraise=True)
        sys.exit(1)
    while True:
        try:
            return get_credentials(config_path, scopes=scopes, cache_path=cache_path, logger=logger)
        except InvalidClientSecretsError as e:
            import webbrowser
            url = "https://console.cloud.google.com/apis/credentials"
            print("please save credentials.json at {!r}.".format(config_path), file=sys.stderr)
            webbrowser.open(url, new=1, autoraise=True)
            input("saved? (if saved, please typing enter key)")


class Loader:
    def __init__(
        self,
        *,
        config_path=DEFAULT_CREDENTIALS_PATH,
        scopes=[SCOPE],
        get_credentials=get_credentials_failback_webbrowser,
        http=None
    ):
        self.config_path = config_path
        self.scopes = scopes
        self.get_credentials = get_credentials
        self.http = http or httplib2.Http()

    @reify
    def service(self):
        credentials = self.get_credentials(self.config_path, scopes=self.scopes)
        return googleapiclient.discovery.build(
            'sheets', 'v4', http=credentials.authorize(self.http)
        )

    def load_sheet(self, guessed, *, with_header=True):
        resource = self.service.spreadsheets()
        if guessed.range is None:
            result = resource.get(spreadsheetId=guessed.spreadsheet_id).execute()
            return [
                {
                    "title": sheet["properties"]["title"],
                    **sheet["properties"]["gridProperties"]
                } for sheet in result.get("sheets") or []
            ]
        else:
            result = resource.values().get(
                spreadsheetId=guessed.spreadsheet_id, range=guessed.range
            ).execute()
            values = result.get("values")
            if not with_header:
                return values
            if not values:
                return values
            headers = values[0]
            return [{k: v for k, v in zip(headers, row)} for row in values[1:]]