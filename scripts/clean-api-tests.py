#!/usr/bin/env python

__copyright__ = "Copyright (c) 2024-2025 Alex Laird"
__license__ = "MIT"

import json
import sys

from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig
from pyngrok.process import capture_run_process


def clean_api_tests(args):
    description = "Created by pyngrok test"

    pyngrok_config = PyngrokConfig()
    ngrok.install_ngrok(pyngrok_config)

    print(f"\nLooking for test resources against the ngrok API that have the description "
          f"\"{description}\" to cleanup ...")

    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "edges", "https", "list"])
    for value in json.loads(output[output.find("{"):])["https_edges"]:
        if value.get("description") == description:
            print(f"--> Deleting test Edge for {value['hostports']}")
            capture_run_process(pyngrok_config.ngrok_path,
                                ["api", "edges", "https", "delete",
                                 value["id"]])

    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "edges", "tcp", "list"])
    for value in json.loads(output[output.find("{"):])["tcp_edges"]:
        if value.get("description") == description:
            print(f"--> Deleting test Edge for {value['hostports']}")
            capture_run_process(pyngrok_config.ngrok_path,
                                ["api", "edges", "tcp", "delete",
                                 value["id"]])

    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "edges", "tls", "list"])
    for value in json.loads(output[output.find("{"):])["tls_edges"]:
        if value.get("description") == description:
            print(f"--> Deleting test Edge for {value['hostports']}")
            capture_run_process(pyngrok_config.ngrok_path,
                                ["api", "edges", "tls", "delete",
                                 value["id"]])

    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "reserved-domains", "list"])
    for value in json.loads(output[output.find("{"):])["reserved_domains"]:
        if value.get("description") == description:
            print(f"--> Deleting test reserved-domain {value['domain']}")
            capture_run_process(pyngrok_config.ngrok_path,
                                ["api", "reserved-domains", "delete",
                                 value["id"]])

    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "reserved-addrs", "list"])
    for value in json.loads(output[output.find("{"):])["reserved_addrs"]:
        if value.get("description") == description:
            print(f"--> Deleting test reserved-addr {value['addr']}")
            capture_run_process(pyngrok_config.ngrok_path,
                                ["api", "reserved-addrs", "delete",
                                 value["id"]])

    print(f"... done!")


if __name__ == "__main__":
    clean_api_tests(sys.argv)
