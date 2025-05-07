#!/usr/bin/env python

__copyright__ = "Copyright (c) 2024-2025 Alex Laird"
__license__ = "MIT"

import getpass
import json
import os
import sys
import time
from random import randint
from subprocess import CalledProcessError

from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig
from pyngrok.process import capture_run_process

description = "Created by pyngrok test"


def create_test_resources(subdomain_prefix="pyngrok-init"):
    """
    Provisioning test resources with the ngrok API, and then setting secrets in the CI environment so the resources are
    shared across tests, can greatly reduce the chances of being rate limited when running a build matrix.
    """
    ensure_api_key_present()

    pyngrok_config = PyngrokConfig()
    ngrok.install_ngrok(pyngrok_config)

    subdomain = os.environ.get("NGROK_SUBDOMAIN", getpass.getuser())
    ngrok_hostname = f"{subdomain}.ngrok.dev"

    try:
        reserve_ngrok_domain(pyngrok_config, ngrok_hostname)
    except CalledProcessError as e:
        output = e.output.decode("utf-8")
        if "domain is already reserved" not in output:
            print("An error occurred: " + e.output.decode("utf-8"))
            sys.exit(1)

    try:
        subdomain = generate_name_for_subdomain(subdomain_prefix)
        hostname = f"{subdomain}.{ngrok_hostname}"
        reserved_domain = reserve_ngrok_domain(pyngrok_config, hostname)

        tcp_edge_reserved_addr = reserve_ngrok_addr(pyngrok_config)
        time.sleep(0.5)
        tcp_edge = create_ngrok_edge(pyngrok_config, "tcp",
                                     *tcp_edge_reserved_addr["addr"].split(":"))

        subdomain = generate_name_for_subdomain(subdomain_prefix)
        http_edge_hostname = f"{subdomain}.{ngrok_hostname}"
        http_edge_reserved_domain = reserve_ngrok_domain(pyngrok_config,
                                                         http_edge_hostname)
        time.sleep(0.5)
        http_edge = create_ngrok_edge(pyngrok_config, "https",
                                      http_edge_hostname, 443)

        subdomain = generate_name_for_subdomain(subdomain_prefix)
        tls_edge_hostname = f"{subdomain}.{ngrok_hostname}"
        tls_edge_reserved_domain = reserve_ngrok_domain(pyngrok_config,
                                                        tls_edge_hostname)
        time.sleep(0.5)
        tls_edge = create_ngrok_edge(pyngrok_config, "tls",
                                     tls_edge_hostname, 443)
    except CalledProcessError as e:
        print("An error occurred: " + e.output.decode("utf-8"))
        sys.exit(1)

    print("--> The following ngrok resources have been provisioned. Set these as GitHub secrets to reduce rate limiting"
          "when running a build matrix.")

    print(f"export NGROK_HOSTNAME={ngrok_hostname}")

    print(f"export NGROK_DOMAIN={reserved_domain['domain']}")
    os.environ["NGROK_DOMAIN"] = reserved_domain["domain"]
    os.environ["NGROK_DOMAIN_ID"] = reserved_domain["id"]

    print(f"export NGROK_TCP_EDGE_ADDR={tcp_edge_reserved_addr['addr']}")
    print(f"export NGROK_TCP_EDGE_ID={tcp_edge['id']}")
    os.environ["NGROK_TCP_EDGE_ADDR"] = tcp_edge_reserved_addr["addr"]
    os.environ["NGROK_TCP_EDGE_ADDR_ID"] = tcp_edge_reserved_addr["id"]
    os.environ["NGROK_TCP_EDGE_ID"] = tcp_edge["id"]

    print(f"export NGROK_HTTP_EDGE_DOMAIN={http_edge_reserved_domain['domain']}")
    print(f"export NGROK_HTTP_EDGE_ID={http_edge['id']}")
    os.environ["NGROK_HTTP_EDGE_DOMAIN"] = http_edge_reserved_domain["domain"]
    os.environ["NGROK_HTTP_EDGE_DOMAIN_ID"] = http_edge_reserved_domain["id"]
    os.environ["NGROK_HTTP_EDGE_ID"] = http_edge["id"]

    print(f"export NGROK_TLS_EDGE_DOMAIN={tls_edge_reserved_domain['domain']}")
    print(f"export NGROK_TLS_EDGE_ID={tls_edge['id']}")
    os.environ["NGROK_TLS_EDGE_DOMAIN"] = tls_edge_reserved_domain["domain"]
    os.environ["NGROK_TLS_EDGE_DOMAIN_ID"] = tls_edge_reserved_domain["id"]
    os.environ["NGROK_TLS_EDGE_ID"] = tls_edge["id"]


def ensure_api_key_present():
    if "NGROK_API_KEY" not in os.environ:
        print("An error occurred: NGROK_API_KEY environment variable must be set to use this script.")
        sys.exit(1)


def generate_name_for_subdomain(prefix):
    return "{prefix}-{random}".format(prefix=prefix, random=randint(1000000000, 2000000000))


def reserve_ngrok_domain(pyngrok_config, domain):
    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "reserved-domains", "create",
                                  "--domain", domain,
                                  "--description", description])
    return json.loads(output[output.find("{"):])


def reserve_ngrok_addr(pyngrok_config):
    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "reserved-addrs", "create",
                                  "--description", description])
    return json.loads(output[output.find("{"):])


def create_ngrok_edge(pyngrok_config, proto, domain, port):
    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "edges", proto, "create",
                                  "--hostports", f"{domain}:{port}",
                                  "--description", description])
    return json.loads(output[output.find("{"):])


if __name__ == "__main__":
    create_test_resources()
