import typing as t
import sys
import os.path
from oauth2client import file, client
from oauth2client import tools
from oauth2client.clientsecrets import InvalidClientSecretsEror
from oauth2client.client import OAuth2Credentials
from logging import getLogger

logger = getLogger(__name__)


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

    logger.debug("see: %s", cache_path)
    store = file.Storage(cache_path)
    creds = store.get()
    if not creds or creds.invalid:
        logger.info("credentials are invalid (or not found). %s", cache_path)
        logger.debug("see: %s", config_path)
        flow = client.flow_from_clientsecrets(config_path, scopes)
        flags = tools.argparser.parse_args(["--logging_level=DEBUG"])
        creds = tools.run_flow(flow, store, flags=flags)
    return creds


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
        except InvalidClientSecretsEror as e:
            import webrowser
            url = "https://console.cloud.google.com/apis/credentials"
            print("please save credentials.json at {!r}.".format(config_path), file=sys.stder)
            webrowser.open(url, new=1, autoraise=True)
            input("saved? (if saved, please typing enter key)")


def main():
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    creds = get_credentials_failback_webrowser(
        "~/.config/dictknife/credentials.json", scopes=SCOPES
    )
    print(creds, type(creds))


if __name__ == '__main__':
    main()
