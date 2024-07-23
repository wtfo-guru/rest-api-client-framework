"""Top level module cli for semaphore-rest-api-client package."""

import sys
import types
from pprint import pprint
from loguru import logger
from typing import NoReturn

import click

from api_client.constants import VERSION
from api_client.endpoint import Endpoint, HTTPMethod
from api_client.request import RestRequest
from technitium_rac.configurator import app_config

CONTEXT_SETTINGS = types.MappingProxyType({"help_option_names": ["-h", "--help"]})
USER_AGENT = "Technitium Rest API Client"


@click.command()
@click.option("--enable/--no-enable", default=False, help="Enable/disable blocking.")
@click.option(
    "-m", "--minutes", "--min", type=int, default=15, help="Specify minutes to disable."
)
def blocking(enable: bool, minutes: int) -> NoReturn:
    """Enable/disable blocking on the technitium server."""

    for server in {"pri"}:
        root, token = app_config.server_info(server)
        q_params = ["token"]
        if enable:
            action = "set"
            name = "enable_blocking"
            q_params.append("enableBlocking")
        else:
            action = "temporaryDisableBlocking"
            name = "disable_blocking"
            q_params.append("minutes")

        endpoint = Endpoint(
            name=name,
            path="/api/settings/{action}",
            request_method=HTTPMethod.GET,
            query_parameters=q_params,
        )
        req = RestRequest(
            endpoints=endpoint,
            api_root=root,
            user_agent=USER_AGENT,
        )
        if enable:
            resp = req.call_endpoint(
                name, action=action, token=token, enable_blocking=True,
            )
        else:
            resp = req.call_endpoint(name, action=action, token=token, minutes=minutes)
        logger.info(resp)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("-d", "--debug", count=True, default=0, help="Bump debug level.")
@click.option("-v", "--verbose", count=True, default=0, help="Bump verbose level.")
@click.version_option(VERSION)
def main(debug: int, verbose: int) -> int:
    """Provide api access to a semaphore server."""
    app_config.options["debug"] = debug
    app_config.options["verbose"] = verbose
    if debug:
        pprint(app_config.model_dump_json())
        print("debug: {0}".format(app_config.debug()))
    return 0


main.add_command(blocking)

if __name__ == "__main__":
    sys.exit(main())  # pragma no cover
