"""Top-level module configurator for wtfimap package."""

import os
import re
import sys
from pathlib import Path
from typing import Tuple
from urllib.parse import urljoin

import click
from pydantic import EmailStr, HttpUrl, SecretStr
from yaml_settings_pydantic import (
    BaseYamlSettings,
    YamlFileConfigDict,
    YamlSettingsConfigDict,
)

_TEST = "test"
_PROJECT = "technitium_rac"
_TECHNITIUM_RAC_ENV = os.getenv("TECHNITIUM_RAC_ENV", "prod")
if _TECHNITIUM_RAC_ENV == _TEST and os.getenv("GL_PIPELINE_FLAG", "NO") == "YES":
    _SETTINGS_FILE = Path("./.ci-config.yaml")
else:
    _SETTINGS_FILE = Path().home() / ".config" / "{0}.yaml".format(_PROJECT)

class Common(BaseYamlSettings):
    """Common configuration parameters."""

    # __env_yaml_files__ = str(Path().home() / ".config" / "{0}.yaml".format(PROJECT))
    # __env_yaml_files__ = "/home/jim/.config/wtfimap.yaml"

    options: dict[str, int | str | bool]
    pri_root: HttpUrl
    pri_token: SecretStr
    sec_root: HttpUrl
    sec_token: SecretStr
    testing: bool = False
    environ: str = "dunno"

    @property
    def debug(self) -> bool:
        """Debug property."""
        return self.options.get("debug", False)

    @property
    def test(self) -> bool:
        """Test property."""
        return self.options.get(_TEST, False)

    @property
    def verbose(self) -> bool:
        """Verbose property."""
        return self.options.get("verbose", False)

    def initialize(self, **kwargs: bool) -> None:
        """Initialize options."""
        for kk, vv in kwargs.items():
            self.options[kk] = vv

    def server_info(self, name: str) -> Tuple[str, str]:
        """Return the server information.

        :param name: Server identifier one of pri or sec
        :type name: str
        :return: The Api root and token for the server
        :rtype: Tuple[HttpUrl, SecretStr]
        """
        if re.match("pri", name, re.IGNORECASE):
            return (str(self.pri_root), self.pri_token.get_secret_value())
        return (str(self.sec_root), self.sec_token.get_secret_value())


class Dev(Common):
    """Configuration parameters for dev environment."""

    model_config = YamlSettingsConfigDict(
        yaml_files={_SETTINGS_FILE: YamlFileConfigDict(subpath="dev", required=True)},
    )


class Test(Common):
    """Configuration parameters for test environment."""

    testing: bool = True

    model_config = YamlSettingsConfigDict(
        yaml_files={_SETTINGS_FILE: YamlFileConfigDict(subpath=_TEST, required=True)},
    )


class Prod(Common):
    """Configuration parameters for prod environment."""

    model_config = YamlSettingsConfigDict(
        yaml_files={_SETTINGS_FILE: YamlFileConfigDict(subpath="prod", required=True)},
    )


_setup = {"dev": Dev, _TEST: Test, "prod": Prod}

# Validate and instantiate specified environment configuration.
try:
    app_config: Dev | Test | Prod
    app_config = _setup[_TECHNITIUM_RAC_ENV]()  # type: ignore[assignment, call-arg]
    # app_config = Test()
except ValueError as ex:
    click.echo(str(ex))
    sys.exit(1)
