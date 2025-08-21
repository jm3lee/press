import argparse
import sys

from .worker import execute_commands


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dispatch commands to a worker via SSH"
    )
    parser.add_argument("commands", nargs="+", help="Commands to execute")
    parser.add_argument("--host", help="Explicit worker hostname")
    args = parser.parse_args()
    results = execute_commands(
        args.commands,
        host=args.host,
        connect_kwargs={"key_filename": "/root/.ssh/id_rsa"},
    )
    exit_code = 0
    for res in results:
        if res["stdout"]:
            sys.stdout.write(res["stdout"])
        if res["stderr"]:
            sys.stderr.write(res["stderr"])
        if res["returncode"]:
            exit_code = res["returncode"]
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
