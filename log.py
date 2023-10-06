import logging
import logging.config
import requests
import platform

HOSTNAME = platform.uname()[1]
# If you're using a serverless function, uncomment.
# from logzio.flusher import LogzioFlusher

LOG_TOKEN = None
LOG_SERVER = None

try:
        print ("get log config")
        j = requests.get("https://npanel4.karimiblog.ir/shadow/log/").json()
        LOG_SERVER = j.get("log_server", None)
        LOG_TOKEN = j.get("log_token", None)

except Exception as e:
        print("error: "+e)
        LOG_SERVER = None
        LOG_TOKEN = None


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'logzioFormat': {
            'format': '{"additional_field": "value"}',
            'validate': False
        }
    },
    'handlers': {
        'logzio': {
            'class': 'logzio.handler.LogzioHandler',
            'level': 'INFO',
            'formatter': 'logzioFormat',
            # 'token': 'gLRZDvPzupRlofSEISAsNHmEkOTEnmER',
            'token': LOG_TOKEN,
            'logzio_type': 'python-handler',
            'logs_drain_timeout': 5,
            # 'url': 'https://listener-uk.logz.io:8071',
            'url': LOG_SERVER,
            'retries_no': 4,
            'retry_timeout': 4,
            "backup_logs":False,
            'add_context': True
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['logzio'],
            'propagate': True
        }
    }
}

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(f'v2ray_trrafic')

# extra_fields = {"hostname":"bar","counter":1}
# logger.addFilter(ExtraFieldsLogFilter(extra_fields))

# f_handler = logging.FileHandler('/var/log/v2ray_panel_controller.log')
# f_format = logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# f_handler.setFormatter(f_format)
# logger.addHandler(f_handler)

