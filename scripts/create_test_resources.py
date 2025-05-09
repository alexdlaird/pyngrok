#!/usr/bin/env python

__copyright__ = "Copyright (c) 2024-2025 Alex Laird"
__license__ = "MIT"

import getpass
import os
import shutil
import subprocess
import sys
import time
from random import randint
from subprocess import CalledProcessError

from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig
from pyngrok.exception import PyngrokNgrokError

project = os.path.basename(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def create_test_resources(temp=False):
    """
    This script will provision test resources with the ngrok API. These can be torn down after each test, or they can
    remain to be reused between tests, which will reduce rate limiting (especially when running a build matrix on CI).
    Set these as environment variables, or secrets in a CI build environment, to reuse them across runs after they're
    provisioned.

    :param temp: Whether the resources being created are for single-use (set up and tear down within a single test
        case run), or are to be persisted (to be set in the environment and used across runs).
    """
    ensure_api_key_present()

    prefix = get_prefix(temp)
    description = get_description(temp)

    pyngrok_config = PyngrokConfig()
    ngrok.install_ngrok(pyngrok_config)

    subdomain = os.environ.get("NGROK_SUBDOMAIN", getpass.getuser())
    ngrok_hostname = f"{subdomain}.ngrok.dev"

    try:
        reserve_ngrok_domain(pyngrok_config, description, ngrok_hostname)
    except PyngrokNgrokError as e:
        if "domain is already reserved" not in str(e):
            raise e

    try:
        subdomain = generate_name_for_subdomain(prefix)
        hostname = f"{subdomain}.{ngrok_hostname}"
        reserved_domain = reserve_ngrok_domain(pyngrok_config, description, hostname)

        tcp_edge_reserved_addr = reserve_ngrok_addr(pyngrok_config, description)
        time.sleep(0.5)
        tcp_edge = create_ngrok_edge(pyngrok_config, description, "tcp", *tcp_edge_reserved_addr["addr"].split(":"))

        subdomain = generate_name_for_subdomain(prefix)
        http_edge_hostname = f"{subdomain}.{ngrok_hostname}"
        http_edge_reserved_domain = reserve_ngrok_domain(pyngrok_config, description, http_edge_hostname)
        time.sleep(0.5)
        http_edge = create_ngrok_edge(pyngrok_config, description, "https", http_edge_hostname, 443)

        subdomain = generate_name_for_subdomain(prefix)
        tls_edge_hostname = f"{subdomain}.{ngrok_hostname}"
        tls_edge_reserved_domain = reserve_ngrok_domain(pyngrok_config, description, tls_edge_hostname)
        time.sleep(0.5)
        tls_edge = create_ngrok_edge(pyngrok_config, description, "tls", tls_edge_hostname, 443)
    except CalledProcessError as e:
        print("An error occurred: " + e.output.decode("utf-8"))
        sys.exit(1)

    if not shutil.which("gh"):
        print("--> The following ngrok resources have been provisioned. Set these as environment variables, or "
              "secrets in a CI build environment, to reduce rate limiting when running a build matrix.")

    env_vars = {
        "NGROK_HOSTNAME": ngrok_hostname,
        "NGROK_DOMAIN": reserved_domain["domain"],
        "NGROK_TCP_EDGE_ADDR": tcp_edge_reserved_addr["addr"],
        "NGROK_TCP_EDGE_ID": tcp_edge["id"],
        "NGROK_HTTP_EDGE_DOMAIN": http_edge_reserved_domain["domain"],
        "NGROK_HTTP_EDGE_ID": http_edge["id"],
        "NGROK_TLS_EDGE_DOMAIN": tls_edge_reserved_domain["domain"],
        "NGROK_TLS_EDGE_ID": tls_edge["id"],
    }

    for key, value in env_vars.items():
        print(f"export {key}={value}")
        if not temp and shutil.which("gh"):
            subprocess.run(["gh", "secret", "set", key, "--body", value])
        # Also set the values in os.environ, so if a testcase is setting up its own resources, it can also tear them
        # down at the end. The exception is NGROK_HOSTNAME, since it is used as the flag to determine if resources
        # were set up to be shared across a build matrix or not (which would indicate the test did not set up its own
        # resources, and thus also shouldn't tear them down when finished).
        if key != "NGROK_HOSTNAME":
            os.environ[key] = value

    # Additional ID vars are needed so a testcase that set up its own resources can also tear them down
    os.environ["NGROK_DOMAIN_ID"] = reserved_domain["id"]
    os.environ["NGROK_TCP_EDGE_ADDR_ID"] = tcp_edge_reserved_addr["id"]
    os.environ["NGROK_HTTP_EDGE_DOMAIN_ID"] = http_edge_reserved_domain["id"]
    os.environ["NGROK_TLS_EDGE_DOMAIN_ID"] = tls_edge_reserved_domain["id"]


def ensure_api_key_present():
    if "NGROK_API_KEY" not in os.environ:
        print("An error occurred: NGROK_API_KEY environment variable must be set to use this script.")
        sys.exit(1)


def get_prefix(temp):
    prefix = project
    if temp:
        prefix += "-temp"
    return prefix


def get_description(temp):
    if temp:
        return f"Created by {project} testcase"
    else:
        return f"Created for {project}"


def generate_name_for_subdomain(prefix):
    return "{prefix}-{random}".format(prefix=prefix, random=randint(1000000000, 2000000000))


def reserve_ngrok_domain(pyngrok_config, description, domain):
    return ngrok.api("reserved-domains", "create",
                     "--domain", domain,
                     "--description", description,
                     pyngrok_config=pyngrok_config).data


def reserve_ngrok_addr(pyngrok_config, description):
    return ngrok.api("reserved-addrs", "create",
                     "--description", description,
                     pyngrok_config=pyngrok_config).data


def create_ngrok_edge(pyngrok_config, description, proto, domain, port):
    return ngrok.api("edges", proto,
                     "create", "--hostports", f"{domain}:{port}",
                     "--description", description,
                     pyngrok_config=pyngrok_config).data


if __name__ == "__main__":
    create_test_resources()
