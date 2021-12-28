#!/usr/bin/env python3

import os, yaml, re, argparse, logging
from pathlib import Path


def build_docker_compose(args):
    def append_label(labels, label, value):
        if label not in labels:
            labels[label] = value
        else:
            labels[label] = ",".join([labels[label], value])

        return labels

    """
    Manage creating of labels necessary for Traefik reverse proxying
    """

    def add_traefik_labels(labels, service_name, service):
        if "auth" not in labels:
            labels["auth"] = True  # default to true
        auth_service = args.auth_service
        auth_middleware = None
        if labels["auth"] == True:
            if auth_service == "organizr":
                # Default auth level to 4 ('User')
                if labels["auth"] == True:
                    auth_middleware = f"{auth_service}-4@docker"
                elif isinstance(labels["auth"], int):
                    auth_middleware = f"{auth_service}-{labels['auth']}@docker"
            else:
                if labels["auth"] == True:
                    auth_middleware = f"{auth_service}@docker"
                elif isinstance(labels["auth"], int):
                    auth_middleware = f"{auth_service}@docker"

        if "port" in labels and "host" in labels:
            service["labels"].update(
                {
                    "host": labels["host"],
                    "traefik.enable": True,
                    f"traefik.http.routers.{service_name}.rule": f"Host(`{labels['host']}`)",
                    f"traefik.http.routers.{service_name}.entrypoints": "websecure",
                    f"traefik.http.routers.{service_name}.tls": "true",
                    f"traefik.http.services.{service_name}.loadbalancer.server.port": labels[
                        "port"
                    ],
                }
            )

            if "protocol" in labels:
                service["labels"][
                    f"traefik.http.services.{service_name}.loadbalancer.server.scheme"
                ] = labels["protocol"]

        if "ingress" in labels:
            for ingress in labels["ingress"]:
                service["labels"].update(
                    {
                        "host": ingress["host"],
                        "traefik.enable": True,
                        f"traefik.http.routers.{service_name}-{ingress['port']}.rule": f"Host(`{ingress['host']}`)",
                        f"traefik.http.routers.{service_name}-{ingress['port']}.entrypoints": "websecure",
                        f"traefik.http.routers.{service_name}-{ingress['port']}.tls": "true",
                        f"traefik.http.routers.{service_name}-{ingress['port']}.service": f"{service_name}-{ingress['port']}",
                        f"traefik.http.services.{service_name}-{ingress['port']}.loadbalancer.server.port": ingress[
                            "port"
                        ],
                    }
                )

                if "protocol" in ingress:
                    service["labels"][
                        f"traefik.http.services.{service_name}-{ingress['port']}.loadbalancer.server.scheme"
                    ] = ingress["protocol"]

                if auth_middleware is not None:
                    service["labels"] = append_label(
                        service["labels"],
                        f"traefik.http.routers.{service_name}-{ingress['port']}.middlewares",
                        auth_middleware,
                    )

            del service["labels"]["ingress"]

        if "custom_response_headers" in labels:
            # custom_headers = dict(header.split('=') for header in service['labels']['custom_headers'])
            for header in service["labels"]["custom_response_headers"]:
                service["labels"][
                    f"traefik.http.middlewares.{service_name}-custom-response-headers.headers.customResponseHeaders.{header}"
                ] = service["labels"]["custom_response_headers"][header]

            service["labels"] = append_label(
                service["labels"],
                f"traefik.http.routers.{service_name}.middlewares",
                f"{service_name}-custom-response-headers",
            )
            del service["labels"]["custom_response_headers"]

        if "custom_request_headers" in labels:
            # custom_headers = dict(header.split('=') for header in service['labels']['custom_headers'])
            for header in service["labels"]["custom_request_headers"]:
                service["labels"][
                    f"traefik.http.middlewares.{service_name}-custom-request-headers.headers.customRequestHeaders.{header}"
                ] = service["labels"]["custom_request_headers"][header]

            service["labels"] = append_label(
                service["labels"],
                f"traefik.http.routers.{service_name}.middlewares",
                f"{service_name}-custom-request-headers",
            )
            del service["labels"]["custom_request_headers"]

        if auth_middleware is not None:
            service["labels"] = append_label(
                service["labels"],
                f"traefik.http.routers.{service_name}.middlewares",
                auth_middleware,
            )

        if service_name == "traefik":
            if auth_service == "organizr":
                # handle all levels of auth
                for x in range(0, 5):
                    service["labels"].update(
                        {
                            f"traefik.http.middlewares.{auth_service}-{x}.forwardauth.address": f"http://organizr/api/v2/auth?group={x}",
                            f"traefik.http.middlewares.{auth_service}-{x}.forwardauth.trustforwardheader": True,
                            f"traefik.http.middlewares.{auth_service}-{x}.forwardauth.authresponseheaders": "Remote-User, Remote-Groups",
                        }
                    )
            else:
                service["labels"].update(
                    {
                        f"traefik.http.middlewares.{auth_service}.forwardauth.address": f"http://authelia:9091/api/verify?rd=https://auth.w00t.cloud",
                        f"traefik.http.middlewares.{auth_service}.forwardauth.trustforwardheader": True,
                        f"traefik.http.middlewares.{auth_service}.forwardauth.authresponseheaders": "Remote-User, Remote-Groups",
                    }
                )

            service["labels"].update(
                {
                    f"traefik.http.routers.{service_name}.tls.certresolver": "cloudflare",
                    f"traefik.http.routers.{service_name}.tls.domains[0].main": "w00t.cloud",
                    f"traefik.http.routers.{service_name}.tls.domains[0].sans": "*.w00t.cloud",
                }
            )

    # Remove existing docker-compose file if it exists
    if os.path.exists("docker-compose.yml"):
        os.remove("docker-compose.yml")

    retval = {
        "version": "2.4",
        "services": {},
    }

    networks = {}

    files = [
        os.path.join(root, name)
        for root, dirs, files in os.walk("./stack")
        for name in files
        if name.endswith((".yml", ".yaml"))
    ]

    # files = [f for f in os.listdir(".") if os.path.isfile(f)]
    for filename in files:
        # Only include `.yml` and `.yaml` files
        if not re.search(r"\.ya?ml$", filename):
            continue

        # Exclude hidden files
        # if re.search(r"^\.", filename):
        #     continue

        logging.debug(f"Reading file ${filename}")
        with open(filename, "r") as fh:
            contents = yaml.load(fh, Loader=yaml.FullLoader)

        # If the contents don't contain YAML (maybe it's all commented out), then skip
        if contents is None:
            logging.debug(f"DISABLED: {filename}")
            continue

        if "networks" in contents:
            networks.update(contents["networks"])

        for service_name in contents["services"]:
            service = contents["services"][service_name]

            # Allow disabling a service via a YAML property (do I even use this anymore?)
            if "enabled" in service:
                if service["enabled"] == False:
                    logging.debug(f"DISABLED: {service}")
                    continue

                del service["enabled"]

            if "labels" in service:
                add_traefik_labels(service["labels"], service_name, service)

            retval["services"][service_name] = service

        if len(networks) > 0:
            retval["networks"] = networks

    return retval


def build_nginx(nginx_dir):
    if nginx_dir is None:
        logging.info("No SWAG directory specified, skipping.")
        return

    if os.path.exists("./reverse-proxy-confs") == False:
        os.system("git clone https://github.com/linuxserver/reverse-proxy-confs")
    else:
        os.system("cd reverse-proxy-confs && git pull")

    with open("docker-compose.yml", "r") as fh:
        contents = yaml.load(fh, Loader=yaml.FullLoader)

    if contents is None:
        logging.error("No docker-compose.yml file found.")
        quit()

    logging.info(f"Removing existing nginx confs from {nginx_dir}...")
    for conf in [
        f for f in os.listdir(nginx_dir) if os.path.isfile(os.path.join(nginx_dir, f))
    ]:
        conf = os.path.join(nginx_dir, conf)

        if re.search(r"\.keep\.", conf):
            continue

        if not re.search(r"\.conf$", conf):
            continue

        os.remove(conf)

    with open("nginx.template") as f:
        template = f.read()

    onlyfiles = [f for f in os.listdir(".") if os.path.isfile(os.path.join(".", f))]
    for filename in onlyfiles:
        if re.search(r"^docker-compose", filename):
            continue
        if not re.search(r"\.ya?ml$", filename):
            continue

        with open(filename, "r") as fh:
            contents = yaml.load(fh, Loader=yaml.FullLoader)

        if contents is None:
            continue

        for service_name in contents["services"]:
            service = contents["services"][service_name]
            if "labels" not in service:
                continue

            conf = None
            labels = service["labels"]

            if "host" in labels:
                labels["host"] = labels["host"].replace(
                    "${SERVER_DOMAIN}", "w00t.cloud"
                )

            # labels = dict(label.split('=') for label in service['labels'])
            template_name = labels["template"] if "template" in labels else service_name

            # first, check our cache directory to see if we already have a template of the service
            if os.path.exists(
                f"./reverse-proxy-confs/{template_name}.subdomain.conf.sample"
            ):
                with open(
                    f"./reverse-proxy-confs/{template_name}.subdomain.conf.sample"
                ) as f:
                    conf = f.read()

            auth_block = None
            if "auth" in labels:
                auth_level = 4 if labels["auth"] == True else labels["auth"]
                auth_block = f"include /config/nginx/proxy-confs/organizr-auth.subfolder.keep.conf; auth_request /auth-{auth_level};"

            if conf is not None:
                conf = re.sub(
                    "server_name\s+.+?;", f"server_name {labels['host']};", conf
                )

                if "port" in labels:
                    conf = re.sub(
                        "upstream_port \d+;", f"upstream_port {labels['port']};", conf
                    )
                if "protocol" in labels:
                    conf = re.sub(
                        "upstream_proto \w+;",
                        f"upstream_proto {labels['protocol']};",
                        conf,
                    )

                # use upstream label, otherwise use service_name to make sure we are using the proper container...
                if "upstream" in labels:
                    conf = re.sub(
                        "upstream_app \w+;", f"upstream_app {labels['upstream']};", conf
                    )
                else:
                    conf = re.sub(
                        "upstream_app \w+;", f"upstream_app {service_name};", conf
                    )

                if auth_block is not None:
                    conf = re.sub("^}", f"{auth_block}\n}}", conf, flags=re.MULTILINE)
            else:
                logging.debug(f"No template found for {service_name}")

            if conf is None and "port" in labels:
                host = labels["host"]
                port = labels["port"]
                protocol = labels["protocol"] if "protocol" in labels else "http"

                conf = template.replace("[[host]]", host)
                conf = conf.replace("[[port]]", str(port))
                conf = conf.replace("[[protocol]]", protocol)
                conf = conf.replace(
                    "[[service]]",
                    labels["upstream"] if "upstream" in labels else service_name,
                )

                conf = conf.replace(
                    "[[forward_auth_server]]",
                    auth_block if auth_block is not None else "",
                )
                conf = conf.replace("[[forward_auth_location]]", "")

            if conf is not None:
                if "nginx_directives" in labels:
                    conf = re.sub(
                        "^}",
                        f"{labels['nginx_directives']}\n}}",
                        conf,
                        flags=re.MULTILINE,
                    )

                with open(
                    os.path.join(nginx_dir, f"{service_name}-generated.subdomain.conf"),
                    "w",
                ) as f:
                    f.write(conf)


def post_up():
    with open("./docker-compose.yml", "r") as fh:
        contents = yaml.load(fh, Loader=yaml.FullLoader)

    for service_name in contents["services"]:
        service = contents["services"][service_name]

        if "labels" not in service:
            continue

        if "post_up" not in service["labels"]:
            continue

        logging.info(f"[{service_name}] RUNNING {service['labels']['post_up']}")
        os.system(service["labels"]["post_up"])


def docker_actions(args):
    stack = build_docker_compose(args)

    # Write all valid services to the docker-compose file
    with open("./docker-compose.yml", "w") as fh:
        yaml.dump(stack, fh, default_flow_style=False)

    return stack


def nginx_actions(args):
    build_nginx(args.conf_dir)
    if args.conf_dir is not None:
        os.system("docker restart swag")


def up_actions(args):
    docker_actions(args)
    nginx_actions(args)

    # check if mergerfs is mounted
    exit_code = os.system("mountpoint -q /mnt/storage")
    if exit_code != 0:
        logging.error("Mountpoint is not present. Exiting.")
        quit(256)

    os.system("docker-compose up -d --remove-orphans")
    post_up()


def add_global_args(parser):
    parser.add_argument(
        "-c",
        "--conf-dir",
        help="SWAG proxy-confs directory",
        default=os.getenv("SWAG_DIR", default=None),
    )
    parser.add_argument(
        "-a",
        "--auth-service",
        help="Specify the auth service to use (organizr, authelia, etc)",
        default="authelia",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbose output",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--project-dir",
        help="Directory of the compose files",
        default="./stack",
    )


parser = argparse.ArgumentParser()
add_global_args(parser)

subparsers = parser.add_subparsers(dest="action")

add_global_args(
    subparsers.add_parser(
        "up", help="Build docker-compose.yml and start all containers"
    )
)
add_global_args(subparsers.add_parser("docker", help="Build docker-compose.yml"))
add_global_args(
    subparsers.add_parser("nginx", help="Create all nginx configs for SWAG")
)
add_global_args(subparsers.add_parser("stop", help="Stop all containers"))
add_global_args(subparsers.add_parser("down", help="Stop and remove all containers"))

scale_parser = subparsers.add_parser(
    "scale", help="Scale one or more containers up or down"
)
scale_parser.add_argument(
    "scale_action", choices=["up", "down"], help="Start or stop the container(s)"
)
scale_parser.add_argument("-n", "--namespace", help="Specify containers by 'namespace'")
scale_parser.add_argument("containers", nargs="*", help="Container(s) to scale")
add_global_args(scale_parser)

add_global_args(subparsers.add_parser("pull", help="Pull latest container images"))
add_global_args(subparsers.add_parser("clean", help="Prune docker files"))
add_global_args(
    subparsers.add_parser("update", help="Pull latest images and bring up the stack")
)

args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.verbose == True else logging.INFO,
    format="%(levelname)s - %(message)s",
)

if args.action is None:
    parser.print_help()
    quit()

if args.action == "up":
    up_actions(args)

if args.action == "docker":
    docker_actions(args)

if args.action == "nginx":
    nginx_actions(args)

if args.action in ["stop", "down"]:
    os.system(f"docker-compose {args.action}")

if args.action == "scale":
    services = docker_actions(args)["services"]

    containers = args.containers
    if args.namespace:
        containers = [
            service_name
            for service_name in services
            if "labels" in services[service_name]
            and "namespace" in services[service_name]["labels"]
            and services[service_name]["labels"]["namespace"] == args.namespace
        ]

    if args.scale_action == "up":
        os.system(f"docker-compose up -d {' '.join(args.containers)}")
    else:
        os.system(f"docker-compose stop {' '.join(args.containers)}")

if args.action in ["pull", "update"]:
    docker_actions(args)
    os.system("docker-compose pull --ignore-pull-failures")

if args.action == "update":
    up_actions(args)
    os.system("docker system prune -af --volumes")

if args.action == "clean":
    os.system("docker system prune -af --volumes")
