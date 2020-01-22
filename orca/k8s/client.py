import abc

from kubernetes import client, config, watch

from orca.common import logger

log = logger.get_logger(__name__)


class ClientFactory(object):

    @staticmethod
    def get_client():
        config.load_incluster_config()
        return client


class ResourceProxy(object):

    def __init__(self, list_fn):
        self._list_fn = list_fn

    def get_all(self):
        return self._list_fn().items

    def watch(self, handler):
        for event in watch.Watch().stream(self._list_fn):
            event_type = event['type']
            event_obj = event['object']
            if event_type == "ADDED":
                handler.on_added(event_obj)
            elif event_type == "MODIFIED":
                handler.on_updated(event_obj)
            elif event_type == "DELETED":
                handler.on_deleted(event_obj)
            else:
                raise Exception("Unknown event type %s" % event_type)

    @staticmethod
    def get(k8s_client, kind):
        if kind == 'pod':
            return ResourceProxy(
                k8s_client.CoreV1Api().list_pod_for_all_namespaces)
        elif kind == 'service':
            return ResourceProxy(
                k8s_client.CoreV1Api().list_service_for_all_namespaces)
        elif kind == 'config_map':
            return ResourceProxy(
                k8s_client.CoreV1Api().list_config_map_for_all_namespaces)
        elif kind == 'secret':
            return ResourceProxy(
                k8s_client.CoreV1Api().list_secret_for_all_namespaces)
        elif kind == 'node':
            return ResourceProxy(
                k8s_client.CoreV1Api().list_node)
        elif kind == 'deployment':
            return ResourceProxy(
                k8s_client.AppsV1Api().list_deployment_for_all_namespaces)
        elif kind == 'replica_set':
            return ResourceProxy(
                k8s_client.ExtensionsV1beta1Api().list_replica_set_for_all_namespaces)
        else:
            raise Exception("Unknown kind %s" % kind)


class EventHandler(abc.ABC):

    @abc.abstractmethod
    def on_added(self, entity):
        """Triggered when a K8S resource is added."""

    @abc.abstractmethod
    def on_updated(self, entity):
        """Triggered when a K8S resource is updated."""

    @abc.abstractmethod
    def on_deleted(self, entity):
        """Triggered when a K8S resource is deleted."""
