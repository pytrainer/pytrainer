import logging
from optparse import OptionParser


def get_options():
    """
    Define usage and accepted options for command line startup
    """
    usage = """usage: %prog [options]

    For more help on valid options try:
       %prog -h """
    parser = OptionParser(usage=usage)
    parser.set_defaults(
        log_level=logging.WARNING,
        validate=False,
        equip=False,
        newgraph=True,
        conf_dir=None,
        log_type="file",
    )
    parser.add_option(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="log_level",
        help="enable logging at debug level",
    )
    parser.add_option(
        "-i",
        "--info",
        action="store_const",
        const=logging.INFO,
        dest="log_level",
        help="enable logging at info level",
    )
    parser.add_option(
        "-w",
        "--warn",
        action="store_const",
        const=logging.WARNING,
        dest="log_level",
        help="enable logging at warning level",
    )
    parser.add_option(
        "--error",
        action="store_const",
        const=logging.ERROR,
        dest="log_level",
        help="enable logging at error level",
    )
    parser.add_option(
        "--valid",
        action="store_true",
        dest="validate",
        help="enable validation of files imported by plugins (details at info or debug logging level) - note plugin must support validation.",
    )
    parser.add_option(
        "--oldgraph",
        action="store_false",
        dest="newgraph",
        help="Turn off new graphing approach",
    )
    parser.add_option(
        "--newgraph",
        action="store_true",
        dest="newgraph",
        help="Deprecated Option: Turn on new graphing approach",
    )
    parser.add_option(
        "--confdir",
        dest="conf_dir",
        help="Specify the directory where application configuration will be stored.",
    )
    parser.add_option(
        "--logtype",
        dest="log_type",
        metavar="TYPE",
        type="choice",
        choices=["file", "console"],
        help="Specify where logging should be output to. TYPE is one of 'file' (default), or 'console'.",
    )
    return parser.parse_args()


def main():
    options, args = get_options()
    from pytrainer.environment import Environment
    environment = Environment(options.conf_dir)
    environment.create_directories()
    import pytrainer.lib.localization

    pytrainer.lib.localization.initialize_gettext()
    from pytrainer.main import pyTrainer

    pytrainer = pyTrainer(options)


if __name__ == "__main__":
    main()
