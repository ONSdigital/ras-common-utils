import json
from os import getenv
from structlog import get_logger

import yaml

logger = get_logger()

def map_dict(d, key_mapper=None, value_mapper=None):
    def ident(x):
        return x
    key_mapper = key_mapper or ident
    value_mapper = value_mapper or ident
    return {key_mapper(k): value_mapper(v) for k, v in d.items()}


def lower_keys(d):
    return map_dict(d, key_mapper=str.lower)


class RasDependencyError(Exception):
    pass


class DependencyProxy:

    def __init__(self, dependency, name):
        self._dependency = lower_keys(dependency)
        self._name = name

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        # TODO: consider converting the value to bool (as feature flags are always true/false)
        k = "{}.{}".format(self._name, item)
        return getenv(k) or self._dependency[item]


class FeaturesProxy:

    def __init__(self, features):
        self._features = features

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        k = "feature.{}".format(item)
        return getenv(k) or self._features.get(item)


class RasConfig():

    _is_cloud_foundry = False

    def __init__(self, config_data):
        # TODO: enable env var override

        self._is_cloud_foundry = False
        self.service = {k: getenv(k, v) for k, v in config_data['service'].items()}
        self._dependencies = lower_keys(config_data.get('dependencies', {}))
        self._features = FeaturesProxy(config_data.get('features', {}))
        logger.debug("RasConfig base object has config_data of: {}".format(config_data))

    def feature(self, name):
        return self._features[name]

    def items(self):
        return self.service.items()

    def dependency(self, k):

        try:
            return DependencyProxy(self._dependencies[k], k)
        except KeyError:
            raise RasDependencyError("Dependency with name '{}' not found.".format(k))

    def dependencies(self):

        return {k: DependencyProxy(self._dependencies[k], k) for k in self._dependencies.keys()}.items()

    def features(self):
        return self._features

    def is_cloud_foundry(self):
        return self._is_cloud_foundry


class CloudFoundryServices:
    def __init__(self, service_data):

        # Extract the Cloud Foundry settings that describe the DB connection which looks like this:
        # {'ras-ps-db': {'host': 'my_long_host_name.rds.amazonaws.com', 'password': 'my_secret_password',
        # 'username': 'my_long_hostname',
        # 'uri': 'postgres://my_username:my_password@my_hostname.rds.amazonaws.com:5432/db3d0u371x4tidjnu', 'db_name': 'my_demo_database'}}

        temp_cloud_foundry_settings = {v['name']: v['credentials']
                        for service_config in service_data.values()
                        for v in service_config}

        self._lookup = {}
        # Grab the first key value and populate the lookup 'acitve_db_connection' private variable
        for key in temp_cloud_foundry_settings:
            self._lookup['active_db_connection'] = temp_cloud_foundry_settings[key]
            break

        logger.debug("CloudFoundryServices _lookup is set at ras-ps-db uri: {}".format(self._lookup['active_db_connection']['uri']))

    def get(self, svc_name):
        logger.debug("CloudFoundryServices get called for svc_name: {}".format(svc_name))
        result = self._lookup[svc_name]
        return result


class RasCloudFoundryConfig(RasConfig):

    def __init__(self, config_data):

        super().__init__(config_data)
        self._is_cloud_foundry = True

        vcap_services = json.loads(getenv('VCAP_SERVICES'))
        logger.debug("Ras common has populated VCAP_SERVICES.")

        self._services = CloudFoundryServices(vcap_services)


    def dependency(self, name):

        try:
            return self._services.get(name)
        except KeyError:
            return super().dependency(name)



def from_yaml_file(path):
    with open(path) as f:
        data = yaml.load(f.read())

    vcap_application = getenv('VCAP_APPLICATION')
    if vcap_application:
        logger.info("Ras common has detected a VCAP application environment variable")
        return RasCloudFoundryConfig(data)
    else:
        logger.info("Ras common has NOT detected a VCAP application. Default config will be used.")
        return RasConfig(data)



