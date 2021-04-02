import logging
import logging.config

import yaml


def logging_setup(config_path='logger/logging.yaml'):

    with open(config_path, 'rt') as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)
