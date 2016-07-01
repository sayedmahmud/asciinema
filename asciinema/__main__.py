import locale
import argparse
import os
import sys

from asciinema import __version__
from asciinema.commands.auth import AuthCommand
from asciinema.commands.record import RecordCommand
from asciinema.commands.play import PlayCommand
from asciinema.commands.upload import UploadCommand
from asciinema.config import Config
from asciinema.api import Api


def positive_float(value):
    value = float(value)
    if value <= 0.0:
        raise argparse.ArgumentTypeError("must be positive")
    return value

def rec_command(args, config):
    api = Api(config.api_url, os.environ.get("USER"), config.api_token)
    return RecordCommand(api, args.filename, args.command, args.title, args.yes, args.quiet, args.max_wait)

def play_command(args, config):
    return PlayCommand(args.filename)

def upload_command(args, config):
    api = Api(config.api_url, os.environ.get("USER"), config.api_token)
    return UploadCommand(api, args.filename)

def auth_command(args, config):
    return AuthCommand(config.api_url, config.api_token)

def main():
    if locale.nl_langinfo(locale.CODESET).upper() != 'UTF-8':
        print("asciinema needs a UTF-8 native locale to run. Check the output of `locale` command.")
        sys.exit(1)

    # create the top-level parser
    parser = argparse.ArgumentParser(
        description="Record and share your terminal sessions, the right way.",
        epilog="""example usage:
  Record terminal and upload it to asciinema.org:
    \x1b[1masciinema rec\x1b[0m
  Record terminal to local file:
    \x1b[1masciinema rec demo.json\x1b[0m

For help on a specifc command run:
  \x1b[1masciinema <command> -h\x1b[0m""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--version', help='show version information', action='store_true')

    subparsers = parser.add_subparsers()

    # create the parser for the "rec" command
    parser_rec = subparsers.add_parser('rec', help='Record terminal session')
    parser_rec.add_argument('-c', '--command', help='command to record, defaults to $SHELL')
    parser_rec.add_argument('-t', '--title', help='title of the asciicast')
    parser_rec.add_argument('-w', '--max-wait', help='limit recorded terminal inactivity to max <sec> seconds (can be fractional)', type=positive_float)
    parser_rec.add_argument('-y', '--yes', help='answer "yes" to all prompts (e.g. upload confirmation)', action='store_true')
    parser_rec.add_argument('-q', '--quiet', help='be quiet, suppress all notices/warnings (implies -y)', action='store_true')
    parser_rec.add_argument('filename', nargs='?', default='')
    parser_rec.set_defaults(func=rec_command)

    # create the parser for the "play" command
    parser_upload = subparsers.add_parser('play', help='Replay terminal session')
    parser_upload.add_argument('filename')
    parser_upload.set_defaults(func=play_command)

    # create the parser for the "upload" command
    parser_upload = subparsers.add_parser('upload', help='Upload locally saved terminal session to asciinema.org')
    parser_upload.add_argument('filename')
    parser_upload.set_defaults(func=upload_command)

    # create the parser for the "auth" command
    parser_auth = subparsers.add_parser('auth', help='Assign local API token to asciinema.org account')
    parser_auth.set_defaults(func=auth_command)

    # parse the args and call whatever function was selected
    args = parser.parse_args()

    if args.version:
        print('asciinema %s' % __version__)
    else:
        if hasattr(args, 'func'):
            command = args.func(args, Config())
            code = command.execute()
            sys.exit(code)
        else:
            parser.print_help()


if __name__ == '__main__':
    main()