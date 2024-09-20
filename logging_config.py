from logging.config import dictConfig


def get_logger(env: str, prod: dict, dev: dict, test: dict, handlers: dict):
    """Gibt die passende Logger-Konfiguration basierend auf dem Environment zurück."""
    # Wähle die passende Logger-Konfiguration basierend auf dem Environment
    logger_config = None 
    
    # choose config based on env 
    match env:
        case "prod":
            logger_config = prod
        case "dev":
            logger_config = dev
        case "test":
            logger_config = test
        case _:
            raise ValueError(f"Unknown environment: {env}")
    
    # hardcode properties
    logger_config["propagate"] = False
    logger_config["handlers"] = handlers
    
    return logger_config

    
def setup_logging(env: str):
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            },
            "colorful": {
                "()": "colorlog.ColoredFormatter",
                "format": "\033[37m\033[3m%(asctime)s\033[0m [%(log_color)s%(levelname)s\033[0m] [%(name)s] %(message)s",
                "datefmt": '%Y-%m-%d %H:%M:%S',
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "CRITICAL": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colorful",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": f"logs/app.{env}.log",
                "formatter": "default",
            },
            "endpoints": {
                "class": "logging.FileHandler",
                "filename": f"logs/endpoints.{env}.log",
                "formatter": "default",
            },
        },
        "loggers": {
            # Logger from the app itself
            "uvicorn": get_logger(env, 
                test={"level": "INFO"}, 
                dev={"level": "INFO"}, 
                prod={"level": "INFO"}, 
                handlers={"console", "file"}
            ),
            "uvicorn.access": get_logger(env, 
                test={"level": "CRITICAL"}, 
                dev={"level": "CRITICAL"}, 
                prod={"level": "CRITICAL"}, 
                handlers={"console", "file"}
            ),
            "app": get_logger(env, 
                test={"level": "INFO"}, 
                dev={"level": "INFO"}, 
                prod={"level": "INFO"}, 
                handlers={"console", "file"}
            ),

            # Session loggers
            "sessions.database": get_logger(env, 
                test={"level": "CRITICAL"},
                dev={"level": "DEBUG"}, 
                prod={"level": "CRITICAL"}, 
                handlers={"console", "file"}
            ),
            "sessions.email": get_logger(env, 
                test={"level": "CRITICAL"},
                dev={"level": "DEBUG"}, 
                prod={"level": "CRITICAL"}, 
                handlers={"console", "file"}
            ),
            "sessions.files": get_logger(env, 
                test={"level": "CRITICAL"},
                dev={"level": "DEBUG"}, 
                prod={"level": "CRITICAL"}, 
                handlers={"console", "file"}
            ),
            "sessions.instagram": get_logger(env, 
                test={"level": "CRITICAL"},
                dev={"level": "DEBUG"}, 
                prod={"level": "CRITICAL"}, 
                handlers={"console", "file"}
            ),

            # routes
            "routes.user": get_logger(env, 
                test={"level": "CRITICAL"},
                dev={"level": "INFO"}, 
                prod={"level": "CRITICAL"}, 
                handlers={"console", "file"}
            ),

            "routes.song": get_logger(env, 
                test={"level": "CRITICAL"},
                dev={"level": "INFO"}, 
                prod={"level": "CRITICAL"}, 
                handlers={"console", "file"}
            ),

            "routes.song": get_logger(env, 
                test={"level": "DEBUG"},
                dev={"level": "INFO"}, 
                prod={"level": "CRITICAL"}, 
                handlers={"console", "file"}
            ),

            # Middleware
            "middleware.access_handler": get_logger(env, 
                test={"level": "CRITICAL"},
                dev={"level": "DEBUG"}, 
                prod={"level": "INFO"}, 
                handlers={"console", "file", "endpoints"}
            ),

            #utils
            "utils.media_manipulation": get_logger(env, 
                test={"level": "CRITICAL"},
                dev={"level": "DEBUG"}, 
                prod={"level": "CRITICAL"}, 
                handlers={"console", "file"}
            ),

            # inside test
            "test.unittest": get_logger(env, 
                test={"level": "DEBUG"},
                dev={"level": "CRITICAL"}, 
                prod={"level": "CRITICAL"}, 
                handlers={"console", "file"}
            ),
        },
    })

