#!/usr/bin/env python3

import os, yaml, re, argparse, logging, json, subprocess


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
            # all services require auth unless set to false
            labels["auth"] = True

        auth_middleware = args.auth_middleware if labels["auth"] == True else None

        # support the 'old' way of doing things, convert port / host to ingress
        if "port" in labels and "host" in labels:
            labels["ingress"] = [
                {
                    "port": labels["port"],
                    "host": labels["host"],
                }
            ]

            if "protocol" in labels:
                labels["ingress"][0]["protocol"] = labels["protocol"]

        if "ingress" in labels:
            for ingress in labels["ingress"]:
                rule = ingress["rule"] if "rule" in ingress else f"Host(`{ingress['host']}`)"
                service["labels"].update(
                    {
                        "host": ingress["host"],
                        "traefik.enable": True,
                        f"traefik.http.routers.{service_name}-{ingress['port']}.rule": rule,
                        # f"traefik.http.routers.{service_name}-{ingress['port']}.entrypoints": "websecure",
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

                if "crowdsec" not in labels or labels["crowdsec"] == True:
                    service["labels"] = append_label(
                        service["labels"],
                        f"traefik.http.routers.{service_name}-{ingress['port']}.middlewares",
                        "traefik-bouncer@file",
                    )

            # if we're exposing port / host, ensure it's in the 'web' network but if no networks
            # already defined, include the default
            if "network_mode" not in service:
                if "networks" not in service:
                    service["networks"] = ["default"]

                if "web" not in service["networks"]:
                    if isinstance(service["networks"], list):
                        service["networks"].append("web")
                    else:
                        service["networks"]["web"] = {}

                service["labels"].update({"traefik.docker.network": "web"})

        if "custom_response_headers" in labels:
            #     # custom_headers = dict(header.split('=') for header in service['labels']['custom_headers'])
            #     for header in service["labels"]["custom_response_headers"]:
            #         service["labels"][
            #             f"traefik.http.middlewares.{service_name}-custom-response-headers.headers.customResponseHeaders.{header}"
            #         ] = service["labels"]["custom_response_headers"][header]

            #     service["labels"] = append_label(
            #         service["labels"],
            #         f"traefik.http.routers.{service_name}.middlewares",
            #         f"{service_name}-custom-response-headers",
            #     )
            del service["labels"]["custom_response_headers"]

        if "custom_request_headers" in labels:
            #     # custom_headers = dict(header.split('=') for header in service['labels']['custom_headers'])
            #     for header in service["labels"]["custom_request_headers"]:
            #         service["labels"][
            #             f"traefik.http.middlewares.{service_name}-custom-request-headers.headers.customRequestHeaders.{header}"
            #         ] = service["labels"]["custom_request_headers"][header]

            #     service["labels"] = append_label(
            #         service["labels"],
            #         f"traefik.http.routers.{service_name}.middlewares",
            #         f"{service_name}-custom-request-headers",
            #     )
            del service["labels"]["custom_request_headers"]

    def add_homepage_labels(labels, service_name, service):
        if "namespace" not in labels or "homepage.disabled" == True:
            return

        if "ingress" in labels:
            service["labels"]["homepage.href"] = f"https://{labels['ingress'][0]['host']}"
        elif "host" in labels:
            service["labels"]["homepage.href"] = f"https://{labels['host']}"
        else:
            return

        service["labels"].update({
            "homepage.group": labels["homepage.group"] if "homepage.group" in labels else labels["namespace"],
            "homepage.name": service_name,
            "homepage.icon": labels["homepage.icon"] if "homepage.icon" in labels else service_name
        })

        if "homepage.widget" in labels and labels["homepage.widget"] == True:
            del labels["homepage.widget"]
            service["labels"].update({
                "homepage.widget.type": service_name,
                "homepage.widget.url": service["labels"]["homepage.href"],
            })


    # Remove existing docker compose file if it exists
    if os.path.exists("docker-compose.yml"):
        os.remove("docker-compose.yml")

    retval = {
        "version": "2",
        "services": {},
    }

    networks = {}

    files = [
        os.path.join(root, name)
        for root, dirs, files in os.walk(args.project_dir)
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

        logging.debug(f"Reading file {filename}")
        with open(filename, "r") as fh:
            contents = yaml.load(fh, Loader=yaml.FullLoader)

        # If the contents don't contain YAML (maybe it's all commented out), then skip
        if contents is None:
            logging.debug(f"DISABLED: {filename}")
            continue

        if "networks" in contents:
            networks.update(contents["networks"])
            del contents["networks"]

        if "services" in contents:
            for service_name in contents["services"]:
                service = contents["services"][service_name]

                # Allow disabling a service via a YAML property (do I even use this anymore?)
                if "enabled" in service:
                    if service["enabled"] == False:
                        logging.debug(f"DISABLED: {service}")
                        continue

                    del service["enabled"]

                if "logging" not in service:
                    service["logging"] = {
                        "driver": "json-file",
                        "options": {
                            "max-size": "10m",
                            "max-file": "3",
                            "tag": "{{.ImageName}}|{{.Name}}",
                        },
                    }

                if "labels" in service:
                    add_traefik_labels(service["labels"], service_name, service)
                    add_homepage_labels(service["labels"], service_name, service)

                    # cleanup - can't leave this here because docker compose doesn't support data structures
                    # in labels...
                    try:
                        del service["labels"]["ingress"]
                    except:
                        pass

                retval["services"][service_name] = service

            del contents["services"]

        if len(networks) > 0:
            retval["networks"] = networks

        retval.update(contents)

    return retval


def build_nginx(nginx_dir, args):
    if nginx_dir is None:
        logging.debug("No SWAG directory specified, skipping.")
        return

    if os.path.exists("./reverse-proxy-confs") == False:
        exec_command("git clone https://github.com/linuxserver/reverse-proxy-confs", args)
    else:
        exec_command("cd reverse-proxy-confs && git pull", args)

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
        if re.search(r"^docker compose", filename):
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


def get_containers_by_label(services, label, value):
    return [
        service_name
        for service_name in services
        if "labels" in services[service_name]
        and label in services[service_name]["labels"]
        and services[service_name]["labels"][label] == value
    ]


def get_containers_by_args(args):
    services = build_stack(args)["services"]

    containers = args.containers
    if args.namespace:
        containers = containers + get_containers_by_label(
            services, "namespace", args.namespace
        )
    if args.label:
        label, value = args.label.split("=")
        containers = containers + get_containers_by_label(services, label, value)

    if not containers:
        if args.containers or args.namespace or args.label:
            logging.error("No containers match the specified criteria")
            quit(1)

        containers = list(services.keys())

    return containers


def post_up(containers, args):
    with open("./docker-compose.yml", "r") as fh:
        contents = yaml.load(fh, Loader=yaml.FullLoader)

    for service_name in contents["services"]:
        if len(containers) > 0 and service_name not in containers:
            continue

        service = contents["services"][service_name]

        if "labels" not in service:
            continue

        if "post_up" not in service["labels"]:
            continue

        logging.info(f"[{service_name}] RUNNING {service['labels']['post_up']}")
        os.system(service["labels"]["post_up"])


def build_stack(args):
    stack = build_docker_compose(args)

    # Write all valid services to the docker compose file
    with open("./docker-compose.yml", "w") as fh:
        yaml.dump(stack, fh, default_flow_style=False)

    return stack


def nginx_actions(args):
    build_nginx(args.conf_dir, args)
    if args.conf_dir is not None:
        exec_command("docker restart swag", args)


def up_actions(state, args):
    nginx_actions(args)

    # check if mergerfs is mounted
    exit_code = exec_command("mountpoint -q /mnt/storage", args)
    if exit_code != 0:
        logging.error("Mountpoint is not present. Exiting.")
        quit(256)

    running_containers = []
    disabled_containers = []
    for service in state:
        if state[service]["enabled"] == True:
            running_containers.append(service)
        else:
            disabled_containers.append(service)

    exec_command(f"docker compose up -d --quiet-pull --remove-orphans {' '.join(running_containers)}", args)

    post_up(running_containers, args)

    if args.no_prune == False:
        logging.info("Pruning disabled containers...")
        exec_command(f"docker compose stop {' '.join(disabled_containers)}", args)


def run_actions(args):
    if args.rm == True:
        exec_command(f"docker compose run --rm {args.container} {args.cmd}", args)
    else:
        exec_command(f"docker compose run {args.container} {args.cmd}", args)


def save_state(state, args):
    if args.ignore_state == True:
        return

    logging.debug("Saving state")
    # state = subprocess.run(
    #     ["docker", "compose", "ps", "--format", "json"], stdout=subprocess.PIPE
    # ).stdout.decode("utf-8")
    with open(".dkr.state", "w") as fh:
        fh.write(json.dumps(state))


def load_state(services):
    state = {}
    if os.path.exists(".dkr.state"):
        with open(".dkr.state") as fh:
            state = json.load(fh)

    for service in services:
        if service not in state:
            # if service isn't in state, assume we want it up
            state["service"] = {
                "enabled": True,
            }

    # clean up state file
    for service in list(state):
        if service not in services:
            del state[service]

    return state


def get_running_containers(state):
    running_containers = []
    for service in state:
        if service[service]["enabled"] == True:
            running_containers.append(service)

    return running_containers

def exec_command(cmd, args):
    print(cmd)
    if args.dry_run == False:
        return os.system(cmd)

    return 0

def add_global_args(parser):
    parser.add_argument(
        # "-c",
        "--conf-dir",
        help="SWAG proxy-confs directory",
        default=os.getenv("SWAG_DIR", default=None),
    )
    parser.add_argument(
        "-a",
        "--auth-middleware",
        help="Specify the traefik auth middleware [default: authelia@docker]",
        default="authelia@docker",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbose output",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--ignore-state",
        help="Skip updating the state file",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--project-dir",
        help="Directory of the compose YAML files (overrides DKR_PROJECT_DIR)",
        default=os.getenv("DKR_PROJECT_DIR", default="./docker"),
    )
    parser.add_argument(
        "-w",
        "--work-dir",
        help="Working directory to run in (overrides DKR_WORK_DIR) [default: dkr.py directory]",
        default=os.getenv(
            "DKR_WORK_DIR", default=os.path.dirname(os.path.realpath(__file__))
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Dry run - don't execute docker commands"
    )


parser = argparse.ArgumentParser()
add_global_args(parser)

subparsers = parser.add_subparsers(dest="action")

######################################################
#                      ACTIONS                       #
######################################################
up_parser = subparsers.add_parser(
    "up", help="Build docker-compose.yml and start all enabled containers"
)
add_global_args(up_parser)
up_parser.add_argument("--no-prune", "-P", action="store_true", help="Do not prune disabled containers")

add_global_args(subparsers.add_parser("build", help="Build docker-compose.yml"))
add_global_args(
    subparsers.add_parser("nginx", help="Create all nginx configs for SWAG")
)
add_global_args(
    subparsers.add_parser("start", help="Start containers (ignores state file)")
)

start_parser = subparsers.add_parser(
    "start", help="Start containers (ignores state file)"
)
stop_parser = subparsers.add_parser("stop", help="Stop containers (ignores state file)")

enable_parser = subparsers.add_parser(
    "enable", help="Enable and start a container in the stack"
)
disable_parser = subparsers.add_parser(
    "disable", help="Disable and stop a container in the stack"
)

pull_parser = subparsers.add_parser("pull", help="Pull latest container images")

logs_parser = subparsers.add_parser("logs", help="View and tail container logs")

depends_on_parser = subparsers.add_parser("depends-on", help="Get all containers that depend on a specified container")
depends_on_parser.add_argument("container", help="Dependency container")

run_parser = subparsers.add_parser(
    "run", help="Run a container with the specified args"
)
run_parser.add_argument("container", help="Container to issue the 'run' command to")
run_parser.add_argument(
    "--rm", action="store_true", help="Remove container after execution"
)
run_parser.add_argument("-c", "--cmd", help="Arguments to pass to the 'run' command")
add_global_args(run_parser)

# shared args for parsers that specify containers
for sub_parser in [
    pull_parser,
    logs_parser,
    start_parser,
    stop_parser,
    enable_parser,
    disable_parser,
]:
    sub_parser.add_argument(
        "-n", "--namespace", help="Specify containers by 'namespace' label"
    )
    sub_parser.add_argument(
        "-l", "--label", help="Specify containers by label key-value pair"
    )
    sub_parser.add_argument(
        "containers", nargs="*", help="Specify containers individually"
    )
    add_global_args(sub_parser)


add_global_args(subparsers.add_parser("clean", help="Prune docker files"))

args = parser.parse_args()

# cd into directory of the script
os.chdir(args.work_dir)

logging.basicConfig(
    level=logging.DEBUG if args.verbose == True else logging.INFO,
    format="%(levelname)s - %(message)s",
)

if args.action is None:
    parser.print_help()
    quit()

services = build_stack(args)
state = load_state(services["services"])

if args.action == "depends-on":
    services = build_stack(args)["services"]
    dependents = []
    for service in services:
        if 'depends_on' not in services[service]:
            continue

        # oncall / phpmyadmin
        if args.container in services[service]['depends_on']:
            dependents.append(services[service]['container_name'])

    print(' '.join(dependents))
    quit()

if args.action == "build":
    quit()

if args.action == "up":
    up_actions(state, args)

if args.action == "nginx":
    nginx_actions(args)

if args.action in ["start", "stop", "enable", "disable"]:
    containers = get_containers_by_args(args)

    if args.action in ["start", "enable"]:
        exec_command(f"docker compose up -d {' '.join(containers)}", args)
        post_up(containers, args)
    elif args.action in ["stop", "disable"]:
        exec_command(f"docker compose stop {' '.join(containers)}", args)
        if args.action == "disable":
            exec_command(f"docker rm {' '.join(containers)}", args)

    if args.action in ["enable", "disable"]:
        for service in containers:
            if service in services["services"]:
                if service not in state:
                    state[service] = {}

                state[service]["enabled"] = args.action == "enable"

if args.action == "pull":
    # TODO: Need to fix this logic, remove disabled onlhy if pulling all?
    containers = get_containers_by_args(args)

    if args.containers or args.namespace or args.label:
        if not containers:
            logging.error("No containers match the specified criteria")
            quit(1)

    # filter out containers that aren't enabled, unless it was specifically stated
    for service in containers.copy(): # there a better way than copy here? can't iterate AND modify, index iteration gets off
        logging.debug(f"Checking if {service} is in state...")
        if service not in state or state[service]["enabled"] == False:
            logging.debug(f"  Service {service} is not in state, removing from pull")
            containers.remove(service)

    if args.dry_run:
        print(", ".join(containers))
    else:
        exec_command(f"docker compose pull --ignore-pull-failures {' '.join(containers)}", args)

if args.action == "logs":
    # TODO: Need to fix this logic, remove disabled onlhy if pulling all?
    containers = get_containers_by_args(args)

    if args.containers or args.namespace or args.label:
        if not containers:
            logging.error("No containers match the specified criteria")
            quit(1)


    # filter out containers that aren't enabled, unless it was specifically stated
    for service in state:
        if service in containers and state[service]["enabled"] == False:
            containers.remove(service)

    exec_command(f"docker compose logs -f --tail 100 {' '.join(containers)}", args)

if args.action == "clean":
    exec_command("docker system prune -af --volumes", args)

if args.action == "run":
    build_stack(args)
    run_actions(args)

save_state(state, args)
