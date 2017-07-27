from flask import Flask as BaseFlask, Config as BaseConfig
from ras_common_utils.ras_config import ras_config
from structlog import get_logger

logger = get_logger()

class Config(BaseConfig):
    """Flask config enhanced with a `from_yaml` method.
        This takes values from a RasConfig config object and copies them into the Flask.Config object.
        The Flask Config object is the standard way you interact with application config data. This places those
        environment variables in the Flask.Config object at run time:

        parms: config - An object containing config from environment variables and a configuration yaml file.
        returns: Flask.Config - A Flask.Config object
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dependency = {}
        self.feature = {}
        self.services = {}

    def from_ras_config(self, config):

        try:
            for k, v in config.items():
                self[k] = v

            for k, v in config.dependencies():
                self.dependency[k] = v

            self.feature = config.features()
            self.is_cloud_foundry = config.is_cloud_foundry()
            self.services = config._services.get('active_db_connection')
        except (AttributeError, KeyError) as e:
            logger.error("Ras common utils can't find Cloud Foundry attributes to populate the Flask. Config object. Error: {}".format(e))

class Flask(BaseFlask):
    """Extended version of `Flask` that implements custom config class"""

    def make_config(self, instance_relative=False):
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        return Config(root_path, self.default_config)
