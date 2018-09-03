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
SCOPE = 'https://www.googleapis.com/auth/spreadsheets'
SCOPE_READONLY = 'https://www.googleapis.com/auth/spreadsheets.readonly'


def get_credentials(
    config_path: t.Optional[str] = None,
    *,
    cache_path: t.Optional[str] = None,
    scopes: t.Sequence[str],
    logger: t.Any = logger,
) -> OAuth2Credentials:
    if config_path is None:
        config_path = DEFAULT_CREDENTIALS_PATH
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
        flags = tools.argparser.parse_args(["--logging_level=DEBUG"])
        credentials = tools.run_flow(flow, store, flags=flags)
    return credentials


def get_credentials_failback_webrowser(
    config_path: str,
    *,
    cache_path: t.Optional[str] = None,
    scopes: t.Optional[t.Sequence[str]] = None,
    logger: t.Any = logger,
) -> OAuth2Credentials:
    if scopes is None:
        import webrowser
        url = "https://developers.google.com/identity/protocols/googlescopes"
        print(
            "please passing scopes: (e.g. 'https://www.googleapis.com/auth/spreadsheets.readonly')\nopening {}...".
            format(url),
            file=sys.stder
        )
        webrowser.open(url, new=1, autoraise=True)
        sys.exit(1)
    while True:
        try:
            return get_credentials(config_path, scopes=scopes, cache_path=cache_path, logger=logger)
        except InvalidClientSecretsError as e:
            import webrowser
            url = "https://console.cloud.google.com/apis/credentials"
            print("please save credentials.json at {!r}.".format(config_path), file=sys.stder)
            webrowser.open(url, new=1, autoraise=True)
            input("saved? (if saved, please typing enter key)")


def parse(pattern: str) -> t.Tuple[str, str]:
    """e.g. '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms#/Class Data!A2:E' """
    splitted = pattern.split("#/", 1)
    if len(splitted) == 1:
        return splitted[0], ""
    else:
        return splitted


class Loader:
    def __init__(self, *, scopes=[SCOPE], get_credentials=get_credentials, http=None):
        self.scopes = scopes
        self.get_credentials = get_credentials
        self.http = http or httplib2.Http()

    @reify
    def service(self):
        credentials = self.get_credentials(scopes=self.scopes)
        return googleapiclient.discovery.build(
            'sheets', 'v4', http=credentials.authorize(self.http)
        )

    def load_sheet(self, pattern):
        sheet_id, range_name = parse(pattern)
        params = {"spreadsheetId": sheet_id}
        if range_name:
            params["range"] = range_name
        result = self.service.spreadsheets().values().get(**params).execute()
        return result.get("values")
