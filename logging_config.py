from logging.config import dictConfig

    
def get_logger(env: str, prod: dict, dev: dict, test: dict):
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

    logger_config["propagate"]  = False
    logger_config["handlers"]   = ["console", "file"]
    
    return logger_config
    
def setup_logging(env: str):
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
            },
            "colorful": {
                "()": "colorlog.ColoredFormatter",
                # Format für farbige Logs: Uhrzeit grau und kursiv, nur [LEVEL] farbig
                "format": "\033[37m\033[3m%(asctime)s\033[0m [%(name)s] [%(log_color)s%(levelname)s\033[0m] %(message)s",
                "datefmt": '%Y-%m-%d %H:%M:%S',
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
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
            },
        },
        "loggers": {
            
            # Logger from the app itself
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            
            # Documenting all access to endpoints
            "endpoints": {
                "handlers": ["endpoints"],
                "level": "INFO",
                "propagate": False,
            },
            
            # modules
            "sessions.database": get_logger(env, 
                test={"level": "WARNING"},
                dev={"level": "DEBUG"}, 
                prod={"level": "WARNING"}, 
            ),
            "sessions.email": get_logger(env, 
                test={"level": "WARNING"},
                dev={"level": "DEBUG"}, 
                prod={"level": "WARNING"}, 
            ),
            "sessions.files": get_logger(env, 
                test={"level": "WARNING"},
                dev={"level": "DEBUG"}, 
                prod={"level": "WARNING"}, 
            ),
            "sessions.instagram": get_logger(env, 
                test={"level": "WARNING"},
                dev={"level": "DEBUG"}, 
                prod={"level": "WARNING"}, 
            ),

            "middleware.access_handler": get_logger(env, 
                test={"level": "WARNING"},
                dev={"level": "DEBUG"}, 
                prod={"level": "WARNING"}, 
            )
        },
    })

