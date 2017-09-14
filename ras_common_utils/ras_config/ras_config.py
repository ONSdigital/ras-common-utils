import json
from os import getenv

import yaml
from structlog import get_logger

from ras_common_utils.ras_error.ras_error import RasError

log = get_logger()

DELIMITER = '_'


class RasConfigurationError(RasError):
    pass


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

    def __init__(self, dependency, name, overrides=None):
        self._dependency = dependency
        self._name = name
        self._overrides = overrides or {}

    def __getattr__(self, item):
        return self[item.upper()]

    def __getitem__(self, item):
        k = "{}{}{}".format(self._name, DELIMITER, item)
        return self._overrides.get(item) or getenv(k) or self._dependency[item]


class CloudFoundryDependencyProxy(DependencyProxy):

    def __getitem__(self, item):
        k = "{}{}{}".format(self._name, DELIMITER, item)
        result = self._overrides.get(item) or getenv(k)
        if result is None:
            raise RasError("Environment value not provided for key {}".format(k))


class FeaturesProxy:

    def __init__(self, features):
        self._features = features

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        k = "FEATURE{}{}".format(DELIMITER, item)
        result = getenv(k) or self._features.get(item)
        try:
            return result.lower() in ('true', 't', 'yes', 'y', '1')
        except AttributeError:
            return result is True


class RasConfig:
    def __init__(self, config_data):
        self.service = {k: getenv(k, v) for k, v in config_data['SERVICE'].items()}
        self._dependencies = config_data.get('DEPENDENCIES', {})
        self._features = FeaturesProxy(config_data.get('FEATURES', {}))

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
        return {k: self.dependency(k) for k in self._dependencies.keys()}.items()

    def features(self):
        return self._features


class CloudFoundryServices:
    def __init__(self, service_data):
        self._lookup = {v['name']: v['credentials']
                        for service_config in service_data.values()
                        for v in service_config}

    def get(self, svc_name):
        result = self._lookup[svc_name]
        return result


def missing_service_vars(services):
    return [k for k, v in services.items() if k not in ('NAME', 'VERSION', 'DEBUG') and v is None]


def missing_dependency_vars(dependencies):
    def is_leaf(v):
        return type(v) is not dict

    def flatten_dependency_keys(dependencies, accum, prefix=None):
        for k, v in dependencies.items():
            new_prefix = DELIMITER.join([prefix, k]) if prefix else k
            if is_leaf(v):
                accum.append(new_prefix)
            else:
                flatten_dependency_keys(v, accum, prefix=new_prefix)

    flat_dependency_keys = []
    flatten_dependency_keys(dependencies, flat_dependency_keys)

    return [k for k in flat_dependency_keys if getenv(k) is None]


class RasCloudFoundryConfig(RasConfig):

    def __init__(self, config_data):
        self.service = {k: getenv(k) for k, v in config_data['SERVICE'].items()}
        missing_vars = missing_service_vars(self.service)

        self._dependencies = config_data.get('DEPENDENCIES', {})
        missing_dependencies = missing_dependency_vars(self._dependencies)

        missing_config = missing_vars + missing_dependencies
        if missing_config:
            raise RasConfigurationError(["Environment value not provided for key {}".format(k) for k in missing_config])

        self._features = FeaturesProxy(config_data.get('FEATURES', {}))

        vcap_services = json.loads(getenv('VCAP_SERVICES'))
        self._services = CloudFoundryServices(vcap_services)

    def dependency(self, k):
        try:
            return CloudFoundryDependencyProxy(self._dependencies[k], k, overrides=self._services.get(k))
        except KeyError:
            return super().dependency(k)


def make(config_data):
    vcap_application = getenv('VCAP_APPLICATION')
    if vcap_application:
        log.info("CloudFoundry detected. Creating CloudFoundry configuration object.")
        return RasCloudFoundryConfig(config_data)
    else:
        log.info("CloudFoundry not detected. Creating standard configuration object.")
        return RasConfig(config_data)


def from_yaml_file(path):
    with open(path) as f:
        data = yaml.load(f.read())

    return make(data)
