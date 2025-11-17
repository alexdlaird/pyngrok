#!/usr/bin/env python

__copyright__ = "Copyright (c) 2024-2025 Alex Laird"
__license__ = "MIT"

import os
import sys
import time
from subprocess import CalledProcessError

from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from scripts.create_test_resources import ensure_api_key_present, get_description  # noqa: E402


def delete_test_resources(temp=False):
    ensure_api_key_present()

    description = get_description(temp)

    pyngrok_config = PyngrokConfig()
    ngrok.install_ngrok(pyngrok_config)

    print(f"Deleting test resources from the ngrok API that have the description \"{description}\" ...")

    try:
        response = ngrok.api("reserved-domains", "list",
                             pyngrok_config=pyngrok_config).data
        for value in response["reserved_domains"]:
            if value.get("description") == description:
                print(f"--> Deleting test reserved-domain {value['domain']}")
                ngrok.api("reserved-domains", "delete", value["id"],
                          pyngrok_config=pyngrok_config)
                time.sleep(0.2)

        response = ngrok.api("reserved-addrs", "list",
                             pyngrok_config=pyngrok_config).data
        for value in response["reserved_addrs"]:
            if value.get("description") == description:
                print(f"--> Deleting test reserved-addr {value['addr']}")
                ngrok.api("reserved-addrs", "delete", value["id"],
                          pyngrok_config=pyngrok_config)
    except CalledProcessError as e:
        print("An error occurred: " + e.output.decode("utf-8"))
        sys.exit(1)

    print("... done!")


if __name__ == "__main__":
    temp = False
    if len(sys.argv) > 1 and sys.argv[1] == "--temp":
        temp = True
    delete_test_resources(temp)
