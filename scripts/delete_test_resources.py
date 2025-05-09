#!/usr/bin/env python

__copyright__ = "Copyright (c) 2024-2025 Alex Laird"
__license__ = "MIT"

import json
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
        output = ngrok.api(pyngrok_config,
                           "edges", "https", "list")
        for value in json.loads(output[output.find("{"):])["https_edges"]:
            if value.get("description") == description:
                print(f"--> Deleting test Edge for {value['hostports']}")
                delete_ngrok_edge(pyngrok_config, "https", value["id"])
                time.sleep(0.2)

        output = ngrok.api(pyngrok_config,
                           "edges", "tcp", "list")
        for value in json.loads(output[output.find("{"):])["tcp_edges"]:
            if value.get("description") == description:
                print(f"--> Deleting test Edge for {value['hostports']}")
                delete_ngrok_edge(pyngrok_config, "tcp", value["id"])
                time.sleep(0.2)

        output = ngrok.api(pyngrok_config,
                           "edges", "tls", "list")
        for value in json.loads(output[output.find("{"):])["tls_edges"]:
            if value.get("description") == description:
                print(f"--> Deleting test Edge for {value['hostports']}")
                delete_ngrok_edge(pyngrok_config, "tls", value["id"])
                time.sleep(0.2)

        output = ngrok.api(pyngrok_config,
                           "reserved-domains", "list")
        for value in json.loads(output[output.find("{"):])["reserved_domains"]:
            if value.get("description") == description:
                print(f"--> Deleting test reserved-domain {value['domain']}")
                release_ngrok_domain(pyngrok_config, value["id"])
                time.sleep(0.2)

        output = ngrok.api(pyngrok_config,
                           "reserved-addrs", "list")
        for value in json.loads(output[output.find("{"):])["reserved_addrs"]:
            if value.get("description") == description:
                print(f"--> Deleting test reserved-addr {value['addr']}")
                release_ngrok_addr(pyngrok_config, value["id"])
    except CalledProcessError as e:
        print("An error occurred: " + e.output.decode("utf-8"))
        sys.exit(1)

    print("... done!")


def delete_ngrok_edge(pyngrok_config, proto, id):
    ngrok.api(pyngrok_config,
              "edges", proto,
              "delete", id)


def release_ngrok_domain(pyngrok_config, id):
    ngrok.api(pyngrok_config,
              "reserved-domains", "delete", id)


def release_ngrok_addr(pyngrok_config, id):
    ngrok.api(pyngrok_config,
              "reserved-addrs", "delete", id)


if __name__ == "__main__":
    temp = False
    if len(sys.argv) > 1 and sys.argv[1] == "--temp":
        temp = True
    delete_test_resources(temp)
