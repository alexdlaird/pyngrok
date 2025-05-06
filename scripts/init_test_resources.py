#!/usr/bin/env python

__copyright__ = "Copyright (c) 2024-2025 Alex Laird"
__license__ = "MIT"

import getpass
import json
import os
import platform
import sys
import time
from random import randint
from subprocess import CalledProcessError

from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig
from pyngrok.process import capture_run_process

description = "Created by pyngrok test"


def init_test_resources():
    pyngrok_config = PyngrokConfig()
    ngrok.install_ngrok(pyngrok_config)

    ngrok_subdomain = os.environ.get("NGROK_SUBDOMAIN", getpass.getuser())
    ngrok_parent_domain = f"{ngrok_subdomain}.ngrok.dev"

    try:
        reserve_ngrok_domain(pyngrok_config, ngrok_parent_domain)
    except CalledProcessError as e:
        output = e.output.decode("utf-8")
        if "domain is already reserved" not in output:
            print("An error occurred: " + e.output.decode("utf-8"))
            sys.exit(1)

    try:
        subdomain = create_unique_subdomain_name("pyngrok")
        domain = f"{subdomain}.{ngrok_parent_domain}"
        reserved_domain = reserve_ngrok_domain(pyngrok_config, domain)

        reserved_addr_tcp_edge = reserve_ngrok_addr(pyngrok_config)
        time.sleep(0.5)
        tcp_edge = create_ngrok_edge(pyngrok_config, "tcp",
                                     *reserved_addr_tcp_edge["addr"].split(":"))

        subdomain = create_unique_subdomain_name("pyngrok")
        http_edge_domain = f"{subdomain}.{ngrok_parent_domain}"
        reserved_domain_http_edge = reserve_ngrok_domain(pyngrok_config,
                                                         http_edge_domain)
        time.sleep(0.5)
        http_edge = create_ngrok_edge(pyngrok_config, "https",
                                      http_edge_domain, 443)

        subdomain = create_unique_subdomain_name("pyngrok")
        tls_edge_domain = f"{subdomain}.{ngrok_parent_domain}"
        reserved_domain_tls_edge = reserve_ngrok_domain(pyngrok_config,
                                                        tls_edge_domain)
        time.sleep(0.5)
        tls_edge = create_ngrok_edge(pyngrok_config, "tls",
                                     tls_edge_domain, 443)
    except CalledProcessError as e:
        print("An error occurred: " + e.output.decode("utf-8"))
        sys.exit(1)

    print(f"export NGROK_PARENT_DOMAIN={ngrok_parent_domain}")

    print(f"export NGROK_DOMAIN={reserved_domain['domain']}")
    os.environ["NGROK_DOMAIN"] = reserved_domain["domain"]

    print(f"export NGROK_TCP_EDGE_ADDR={reserved_addr_tcp_edge['addr']}")
    print(f"export NGROK_TCP_EDGE_ID={tcp_edge['id']}")
    os.environ["NGROK_TCP_EDGE_ADDR"] = reserved_addr_tcp_edge["addr"]
    os.environ["NGROK_TCP_EDGE_ID"] = tcp_edge["id"]

    print(f"export NGROK_HTTP_EDGE_DOMAIN={reserved_domain_http_edge['domain']}")
    print(f"export NGROK_HTTP_EDGE_ID={http_edge['id']}")
    os.environ["NGROK_HTTP_EDGE_DOMAIN"] = reserved_domain_http_edge["domain"]
    os.environ["NGROK_HTTP_EDGE_ID"] = http_edge["id"]

    print(f"export NGROK_TLS_EDGE_DOMAIN={reserved_domain_tls_edge['domain']}")
    print(f"export NGROK_TLS_EDGE_ID={tls_edge['id']}")
    os.environ["NGROK_TLS_EDGE_DOMAIN"] = reserved_domain_tls_edge["domain"]
    os.environ["NGROK_TLS_EDGE_ID"] = tls_edge["id"]


def create_unique_subdomain_name(prefix):
    return "{prefix}-{random}-{system}-{python_version}-{sys_major_version}-{sys_minor_version}".format(
        prefix=prefix,
        random=randint(1000000000, 2000000000),
        system=platform.system().lower(),
        python_version=platform.python_implementation().lower(),
        sys_major_version=sys.version_info[0],
        sys_minor_version=sys.version_info[1])


def reserve_ngrok_domain(pyngrok_config, domain):
    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "reserved-domains", "create",
                                  "--domain", domain,
                                  "--description", "Created by pyngrok test"])
    return json.loads(output[output.find("{"):])


def reserve_ngrok_addr(pyngrok_config):
    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "reserved-addrs", "create",
                                  "--description", "Created by pyngrok test"])
    return json.loads(output[output.find("{"):])


def create_ngrok_edge(pyngrok_config, proto, domain, port):
    output = capture_run_process(pyngrok_config.ngrok_path,
                                 ["api", "edges", proto, "create",
                                  "--hostports", f"{domain}:{port}",
                                  "--description", "Created by pyngrok test"])
    return json.loads(output[output.find("{"):])


if __name__ == "__main__":
    init_test_resources()
