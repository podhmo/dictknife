import typing as t
import sys
import os.path
import logging
import pickle
from google_auth_oauthlib import flow
from google.oauth2.credentials import Credentials
from dictknife.langhelpers import reify

from googleapiclient.discovery_cache.base import Cache

# from googleapiclient.discovery_cache import LOGGER as noisy_logger
# # supress stderr message of 'ImportError: file_cache is unavailable when using oauth2client >= 4.0.0 or google-auth' # noqa
# noisy_logger.setLevel(logging.ERROR)  # noqa
import googleapiclient.discovery

logger = logging.getLogger(__name__)

DEFAULT_CREDENTIALS_PATH = "~/.config/dictknife/google-client-secrets.json"
DEFAULT_DISCOVERY_CACHE_PATH = "~/.config/dictknife/discovery.pickle"

# Authorize using one of the following scopes:
#     'https://www.googleapis.com/auth/drive'
#     'https://www.googleapis.com/auth/drive.file'
#     'https://www.googleapis.com/auth/drive.readonly'
#     'https://www.googleapis.com/auth/spreadsheets'
#     'https://www.googleapis.com/auth/spreadsheets.readonly'
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SCOPE_READONLY = "https://www.googleapis.com/auth/spreadsheets.readonly"


def get_credentials(
    config_path: str,
    *,
    cache_path: t.Optional[str] = None,
    scopes: t.Sequence[str],
    logger: t.Any = logger,
    launch_browser: bool = True,
) -> Credentials:
    config_path = os.path.expanduser(config_path)
    if cache_path is None:
        cache_path = os.path.join(os.path.dirname(config_path), "google-token.json")
    cache_path = os.path.expanduser(cache_path)

    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    logger.debug("see: %s", cache_path)
    try:
        credentials = Credentials.from_authorized_user_file(cache_path, scopes=scopes)
        if credentials.valid:
            return credentials

        # todo: refresh token
        from google.auth.transport.requests import Request

        credentials.refresh(Request())  # xxx
        if credentials.valid:
            return credentials
    except FileNotFoundError:
        pass

    logger.info("credentials are invalid (or not found). %s", cache_path)
    logger.debug("see: %s", config_path)
    appflow = flow.InstalledAppFlow.from_client_secrets_file(config_path, scopes=scopes)

    if launch_browser:
        appflow.run_local_server()
    else:
        appflow.run_console()

    with open(cache_path, "w") as wf:
        wf.write(appflow.credentials.to_json())
    return appflow.credentials


def get_credentials_failback_webbrowser(
    config_path: str,
    *,
    cache_path: t.Optional[str] = None,
    scopes: t.Optional[t.Sequence[str]] = None,
    logger: t.Any = logger,
) -> Credentials:
    if scopes is None:
        import webbrowser

        url = "https://developers.google.com/identity/protocols/googlescopes"
        print(
            "please passing scopes: (e.g. 'https://www.googleapis.com/auth/spreadsheets.readonly')\nopening {}...".format(
                url
            ),
            file=sys.stderr,
        )
        webbrowser.open(url, new=1, autoraise=True)
        sys.exit(1)
    while True:
        try:
            return get_credentials(
                config_path, scopes=scopes, cache_path=cache_path, logger=logger
            )
        except (FileNotFoundError, ValueError) as e:
            logger.warn("excpetion %r", e)
            import webbrowser

            url = "https://console.cloud.google.com/apis/credentials"
            print(
                "please save fileat {!r} (OAuth 2.0 client ID)".format(config_path),
                file=sys.stderr,
            )
            webbrowser.open(url, new=1, autoraise=True)
            input("saved? (if saved, please typing enter key)")


class MemoryCache(Cache):
    def __init__(self):
        self.cache = {}

    def get(self, url):
        return self.cache.get(url)

    def set(self, url, content):
        self.cache[url] = content

    @property
    def is_empty(self):
        return len(self.cache) == 0


def _get_discovery_cache(path):
    if not os.path.exists(path):
        return MemoryCache()

    with open(path, "rb") as rf:
        return pickle.load(rf)


class Loader:
    def __init__(
        self,
        *,
        config_path=DEFAULT_CREDENTIALS_PATH,
        discovery_cache_path=DEFAULT_DISCOVERY_CACHE_PATH,
        scopes=[SCOPE],
        get_credentials=get_credentials_failback_webbrowser,
        http=None,
    ):
        self.config_path = os.path.expanduser(config_path)
        self.discovery_cache_path = os.path.expanduser(discovery_cache_path)
        self.scopes = scopes
        self.get_credentials = get_credentials

    @reify
    def cache(self):
        return _get_discovery_cache(self.discovery_cache_path)

    def _save_cache(self, cache):
        with open(self.discovery_cache_path, "wb") as wf:
            pickle.dump(cache, wf)

    @reify
    def service(self):
        need_save = self.cache.is_empty
        credentials = self.get_credentials(self.config_path, scopes=self.scopes)
        service = googleapiclient.discovery.build(
            "sheets", "v4", credentials=credentials, cache=self.cache
        )
        if need_save:
            self._save_cache(self.cache)
        return service

    def load_sheet(self, guessed, *, with_header=True):
        resource = self.service.spreadsheets()

        range_value = guessed.range
        if range_value is None:
            result = resource.get(spreadsheetId=guessed.spreadsheet_id).execute()
            for sheet in result.get("sheets"):
                if str(sheet["properties"]["sheetId"]) == guessed.sheet_id:
                    range_value = sheet["properties"]["title"]
                    break
            if range_value is None:
                return [
                    {
                        "title": sheet["properties"]["title"],
                        **sheet["properties"]["gridProperties"],
                    }
                    for sheet in result.get("sheets") or []
                ]

        result = (
            resource.values()
            .get(spreadsheetId=guessed.spreadsheet_id, range=range_value)
            .execute()
        )
        values = result.get("values")
        if not with_header:
            return values
        if not values:
            return values
        headers = values[0]
        return [{k: v for k, v in zip(headers, row)} for row in values[1:]]

        result = resource.get(spreadsheetId=guessed.spreadsheet_id).execute()
