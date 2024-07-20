"""Top level module cli for semaphore-rest-api-client package."""

import sys
import types
from pprint import pprint
from typing import NoReturn

import click

from api_client.endpoint import Endpoint, HTTPMethod
from api_client.constants import VERSION
from api_client.request import RestRequest

from technitium_rac.configurator import app_config

CONTEXT_SETTINGS = types.MappingProxyType({"help_option_names": ["-h", "--help"]})
USER_AGENT = "Technitium Rest API Client"

@click.command()
@click.option("--enable/--no-enable", default=False, help="Enable/disable blocking.")
@click.option(
    "-m", "--min", "--minutes", type=int, default=15, help="Specify minutes to disable."
)
def blocking(enable: bool, minutes: int) -> NoReturn:
    """Enable/disable blocking on the technitium server."""

    for server in ("pri"):
        root, token = app_config.server_info(server)
        q_params = { "token": token.get_secret_value() }
        if enable:
            action = "set"
            name = "enable_blocking"
            q_params["enableBlocking"] = "true"
        else:
            action = "temporaryDisableBlocking"
            name = "disable_blocking"
            q_params["minutes"] = str(minutes)

        endpoint = Endpoint(
            name=name,
            path="/api/settings/{action}",
            method=HTTPMethod.GET,
            query_parameters=q_params
        )
        rr = RestRequest(endpoints=endpoint, api_root=root.full_string, user_agent=USER_AGENT)




@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("-d", "--debug", count=True, default=0, help="Bump debug level.")
@click.option("-v", "--verbose", count=True, default=0, help="Bump verbose level.")
@click.version_option(VERSION)
def main(debug: int, verbose: int) -> int:
    """Provide api access to a semaphore server."""
    app_config.options["debug"] = debug
    app_config.options["verbose"] = verbose
    if debug:
        pprint(app_config.dict())
        print("debug: {0}".format(app_config.debug()))
    return 0


main.add_command(blocking)

if __name__ == "__main__":
    sys.exit(main())  # pragma no cover
