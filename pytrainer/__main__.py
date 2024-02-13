import logging
import logging.handlers
import sys
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


def set_logging_level(level):
    """Set level of information written to log"""
    logging.debug("Setting logger to level: %s", level)
    logging.getLogger("").setLevel(level)
    logging.getLogger("sqlalchemy.engine").setLevel(level)


def set_logging(level, log_type, environment):
    """Setup rotating log file with customized format"""
    logging.captureWarnings(True)
    if "console" == log_type:
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.handlers.RotatingFileHandler(
            environment.log_file, maxBytes=100000, backupCount=5
        )
    formatter = logging.Formatter(
        "%(asctime)s|%(levelname)s|%(module)s|%(funcName)s|%(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger("").addHandler(handler)
    set_logging_level(level)


def main():
    options, args = get_options()
    from pytrainer.environment import Environment

    environment = Environment(options.conf_dir)
    environment.create_directories()
    set_logging(options.log_level, options.log_type, environment)
    import pytrainer.lib.localization

    pytrainer.lib.localization.initialize_gettext()
    from pytrainer.main import pyTrainer

    pytrainer = pyTrainer(options)


if __name__ == "__main__":
    main()
