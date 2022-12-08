#!/usr/bin/env python3
import argparse
import subprocess
import sys
from uuid import uuid4
from time import sleep


def sys_command(command):
    if isinstance(command, str):
        command = command.split()
    popen = subprocess.Popen(command, stdout=subprocess.PIPE)
    lines_iterator = iter(popen.stdout.readline, b"")
    output = None
    for line in lines_iterator:
        if output is None:
            output = [line]
        else:
            output.append(line)
    return output


def get_all_screens():
    raw_output = sys_command("screen -ls")
    screens = []
    for line in raw_output:
        if not line.startswith(b"\t"):
            continue
        screen = line.decode().strip().split("\t")[0]
        num, name = screen.split(".")
        screen = Screen(name, existing=True)
        screen.id = int(num)
        screens.append(screen)
    return screens


def get_screen_by_name(name):
    for screen in get_all_screens():
        if name == screen.name:
            return screen
    return None


def read_procfile():
    services = []
    try:
        with open("./Procfile") as f:
            lines = f.readlines()
        for line in lines:
            name, command = line.split(":", maxsplit=1)
            services.append({"name": name, "command": command.strip()})
    except FileNotFoundError:
        pass
    return services


class Screen():
    id = None

    def __init__(self, name, existing=False):
        self.name = name
        if not existing:
            if get_screen_by_name(name):
                raise NameError("Screen with this name already exists")
            self.start()

    def start(self):
        sys_command(["screen", "-dmS", self.name])
        for screen in get_all_screens():
            if screen.name == self.name:
                self.id = screen.id

    def connect(self):
        sys_command(["screen", "-r", self.name])

    def screen_command(self, *args):
        sys_command(["screen", "-S", self.name, "-X", *args])

    def kill(self):
        self.screen_command("stuff", "^Z")
        self.screen_command("stuff", "kill -9 %^M")
        self.screen_command("quit")

    def quit(self):
        self.screen_command("stuff", "^C")
        self.screen_command("stuff", "exit^M")

    def tail(self, limit):
        uuid = str(uuid4())
        self.screen_command("hardcopy", "-h", f"/tmp/spm{uuid}")
        try:
            with open(f"/tmp/spm{uuid}", "rb") as f:
                lines = f.readlines()
                while lines and lines[-1].strip() == b"":
                    lines.pop()
                lines = lines[-limit:]
                lines = b"".join(lines)
                return lines.decode("utf-8", errors="replace").strip()
        except FileNotFoundError:
            return None

    def __repr__(self):
        return f"{self.id} {self.name}"


class SPM():
    @staticmethod
    def start(args):
        services_info = read_procfile()
        all_services = [s["name"] for s in services_info]
        services = all_services
        if args["names"]:
            services = args["names"]
        if "exclude" in args and args["exclude"]:
            services = [s for s in services if s not in args["exclude"]]
        for service in services:
            if get_screen_by_name(service):
                print(f"Service '{service}' is already running")
            elif service not in all_services:
                print(f"Service '{service}' does not exist")
            else:
                command = [
                    s["command"] for s in services_info if s["name"] == service
                ][0]
                screen = Screen(service)
                screen.screen_command("stuff", "source .env^M")
                screen.screen_command("stuff", f"{command}^M")
                print(f"Service '{service}' was started")

    @staticmethod
    def restart(args):
        services_info = read_procfile()
        all_services = [s["name"] for s in services_info]
        services = all_services
        if args["names"]:
            services = args["names"]
        if "exclude" in args and args["exclude"]:
            services = [s for s in services if s not in args["exclude"]]
        for service in services:
            if args["kill"]:
                SPM.kill({"names": [service]})
            else:
                SPM.quit({"names": [service], "timeout": args["timeout"]})
            SPM.start({"names": [service]})

    @staticmethod
    def quit(args):
        services_info = read_procfile()
        all_services = [s["name"] for s in services_info]
        services = all_services
        if args["names"]:
            services = args["names"]
        for service in services:
            screen = get_screen_by_name(service)
            if screen:
                screen.quit()
                print(f"Service '{service}' was requested to quit")
                timer = 0
                while get_screen_by_name(service) and timer < args["timeout"]:
                    timer += 1
                    print(
                        f"\rWaiting for '{service}' to close for "
                        f"{timer} seconds", end="")
                    sleep(1)
                if timer:
                    print()
                if get_screen_by_name(service):
                    SPM.kill({"names": [service]})
                else:
                    print(f"Quit '{service}' successfully")
            elif service not in all_services:
                print(f"Service '{service}' does not exist")
            else:
                print(f"Service '{service}' is not running")

    @staticmethod
    def kill(args):
        services_info = read_procfile()
        all_services = [s["name"] for s in services_info]
        services = all_services
        if args["names"]:
            services = args["names"]
        for service in services:
            screen = get_screen_by_name(service)
            if screen:
                screen.kill()
                print(f"Service '{service}' was killed")
            elif service not in all_services:
                print(f"Service '{service}' does not exist")
            else:
                print(f"Service '{service}' is not running")

    @staticmethod
    def connect(args):
        services_info = read_procfile()
        all_services = [s["name"] for s in services_info]
        name = args["name"]
        screen = get_screen_by_name(name)
        if screen:
            screen.connect()
        elif name not in all_services:
            print(f"Service '{name}' does not exist")
        else:
            print(f"Service '{name}' is not running")

    @staticmethod
    def list(_args):
        services_info = read_procfile()
        all_services = [s["name"] for s in services_info]
        for service in all_services:
            screen = get_screen_by_name(service)
            if screen:
                print(f"{service} running")
            else:
                print(f"{service} stopped")

    @staticmethod
    def tail(args):
        services_info = read_procfile()
        all_services = [s["name"] for s in services_info]
        services = all_services
        if args["names"]:
            services = args["names"]
        for service in services:
            screen = get_screen_by_name(service)
            if screen:
                lines = screen.tail(args["lines"])
                if lines:
                    print(f"\n = {service}\n")
                    print(lines)
                else:
                    print(f"\n = {service} has no logging yet\n")
            elif service not in all_services:
                print(f"Service '{service}' does not exist")


def namespace_to_dict(namespace):
    return {
        k: namespace_to_dict(v) if isinstance(v, argparse.Namespace) else v
        for k, v in vars(namespace).items() if k != "sub"
    }


def main():
    parser = argparse.ArgumentParser(
        description="The lightweight Screen Procfile Manager")
    sub = parser.add_subparsers(
        title="sub-commands", dest="sub",
        description="All the valid sub-commands to manage services")
    # Start
    sub_start = sub.add_parser(
        "start", aliases=["s"], help="Start all or some services",
        description="Provide some names to start them, or start all")
    sub_start.add_argument(
        "--exclude", "-e", action="append",
        help="Exclude some services from starting")
    sub_start.add_argument(
        "names", nargs="*",
        help="Service names to start, cannot be combined with excluding")
    # Restart
    sub_restart = sub.add_parser(
        "restart", aliases=["r"], help="Restart all or some services",
        description="Provide some names to restart them, or restart all")
    sub_restart.add_argument(
        "--kill", "-k", action="store_true",
        help="Kill services before starting them again instead of quitting")
    sub_restart.add_argument(
        "--timeout", "-t", default=5, type=int,
        help="Timeout to give services to quit before killing them")
    sub_restart.add_argument(
        "names", nargs="*", help="Service names to restart")
    # Quit
    sub_quit = sub.add_parser(
        "quit", aliases=["q"], help="Quit all or some services",
        description="Provide some names to quit them, or quit all")
    sub_quit.add_argument(
        "--timeout", "-t", default=5, type=int,
        help="Timeout to give services to quit before killing them")
    sub_quit.add_argument("names", nargs="*", help="Service names to quit")
    # Kill
    sub_kill = sub.add_parser(
        "kill", aliases=["k"], help="Kill all or some services",
        description="Provide some names to kill them, or kill all")
    sub_kill.add_argument("names", nargs="*", help="Service names to kill")
    # Connect
    sub_connect = sub.add_parser(
        "connect", aliases=["c"], help="Connect to the shell of a service",
        description="Provide a service name and connect to it interactively")
    sub_connect.add_argument("name", help="Service name to connect to")
    # Help
    sub.add_parser(
        "help", aliases=["h"], help="Show this help and exit",
        description="Show this help and exit")
    # List
    sub.add_parser(
        "list", aliases=["l"], help="Show a list of services with status",
        description="Each service in the Procfile will be listed with status")
    # Tail
    sub_tail = sub.add_parser(
        "tail", aliases=["t"], help="Show the tail of logs from a service",
        description="Shows the last x lines of a service logging, default 50")
    sub_tail.add_argument(
        "names", nargs="*", help="Service names to show logs for")
    sub_tail.add_argument(
        "--lines", "-l", default=50, type=int,
        help="Amount of log lines to show per service, default 50")
    # Parse and run
    args = parser.parse_args()
    if not args or not args.sub or args.sub in ["h", "help"]:
        parser.print_help()
        sys.exit(0)
    short_to_long_names = {
        "s": "start",
        "r": "restart",
        "q": "quit",
        "k": "kill",
        "c": "connect",
        "l": "list",
        "t": "tail"
    }
    long_name = short_to_long_names.get(args.sub, args.sub)
    getattr(SPM, long_name)(namespace_to_dict(args))


if __name__ == "__main__":
    main()
