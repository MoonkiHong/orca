import abc
import enum
import uuid

import addict as dictlib

from orca.common import logger

log = logger.get_logger(__name__)


class GraphObject(abc.ABC):

    def __init__(self, id, properties):
        super().__init__()
        self.id = id
        self.properties = dictlib.Dict(properties)


class Node(GraphObject):

    def __init__(self, id, properties, origin, kind):
        super().__init__(id, properties)
        self.origin = origin
        self.kind = kind

    def __repr__(self):
        return "<Node id=%s properties=%s kind=%s>" % (
            self.id, self.properties, self.kind)


class Link(GraphObject):

    def __init__(self, id, properties, source, target):
        super().__init__(id, properties)
        self.source = source
        self.target = target

    def __repr__(self):
        return "<Link id=%s properties=%s source=%s target=%s>" % (
            self.id, self.properties, self.source.id, self.target.id)


class Graph(object):

    def __init__(self, driver):
        self._driver = driver
        self._listeners = []

    def get_nodes(self, origin=None, kind=None, properties=None):
        return self._driver.get_nodes(origin, kind, properties)

    def get_node(self, id, origin=None, kind=None, properties=None):
        return self._driver.get_node(id, origin, kind, properties)

    def add_node(self, node):
        log.debug("Adding node: %s", node)
        if self.get_node(node.id):
            return
        self._driver.add_node(node)
        self._notify_listeners(GraphEvent.NODE_ADDED, node)

    def update_node(self, node):
        log.debug("Updating node: %s", node)
        self._driver.update_node(node)
        self._notify_listeners(GraphEvent.NODE_UPDATED, node)

    def delete_node(self, node):
        log.debug("Deleting node: %s", node)
        links = self._driver.get_node_links(node)
        for link in links:
            self._driver.delete_link(link)
        self._driver.delete_node(node)
        self._notify_listeners(GraphEvent.NODE_DELETED, node)

    def get_links(self, properties=None):
        return self._driver.get_links(properties)

    def get_link(self, id, properties=None):
        return self._driver.get_link(id, properties)

    def add_link(self, link):
        log.debug("Adding link: %s", link)
        if self.get_link(link.id):
            return
        self._driver.add_link(link)
        self._notify_listeners(GraphEvent.LINK_ADDED, link)

    def update_link(self, link):
        log.debug("Updating link: %s", link)
        self._driver.update_link(link)
        self._notify_listeners(GraphEvent.LINK_UPDATED, link)

    def delete_link(self, link):
        log.debug("Deleting link: %s", link)
        self._driver.delete_link(link)
        self._notify_listeners(GraphEvent.LINK_DELETED, link)

    def get_node_links(self, node, origin=None, kind=None):
        return self._driver.get_node_links(node, origin, kind)

    def add_listener(self, listener):
        self._listeners.append(listener)

    def _notify_listeners(self, event_type, graph_obj):
        for listener in self._listeners:
            if event_type == GraphEvent.NODE_ADDED:
                listener.on_node_added(graph_obj)
            elif event_type == GraphEvent.NODE_UPDATED:
                listener.on_node_updated(graph_obj)
            elif event_type == GraphEvent.NODE_DELETED:
                listener.on_node_deleted(graph_obj)
            elif event_type == GraphEvent.LINK_ADDED:
                listener.on_link_added(graph_obj)
            elif event_type == GraphEvent.LINK_UPDATED:
                listener.on_link_updated(graph_obj)
            elif event_type == GraphEvent.LINK_DELETED:
                listener.on_link_deleted(graph_obj)
            else:
                raise Exception("Unknown event type: %s" % event_type)

    @staticmethod
    def create_node(id, properties, origin, kind):
        return Node(id, properties, origin, kind)

    @staticmethod
    def create_link(properties, source, target):
        id = Graph.generate_id(source.id, target.id)
        return Link(id, properties, source, target)

    @staticmethod
    def generate_id(*names):
        if names:
            namespace = uuid.NAMESPACE_OID
            name = "/".join([str(name) for name in names])
            id = uuid.uuid5(namespace, name)
        else:
            id = uuid.uuid4()
        return str(id)


class GraphEvent(enum.Enum):

    NODE_ADDED = 1
    NODE_UPDATED = 2
    NODE_DELETED = 3
    LINK_ADDED = 4
    LINK_UPDATED = 5
    LINK_DELETED = 6


class EventListener(abc.ABC):

    def __init__(self, graph):
        super().__init__()
        self._graph = graph

    @abc.abstractmethod
    def on_node_added(self, node):
        """Callback triggered when graph node is added."""

    @abc.abstractmethod
    def on_node_updated(self, node):
        """Callback triggered when graph node is updated."""

    @abc.abstractmethod
    def on_node_deleted(self, node):
        """Callback triggered when graph node is deleted."""

    @abc.abstractmethod
    def on_link_added(self, link):
        """Callback triggered when graph link is added."""

    @abc.abstractmethod
    def on_link_updated(self, link):
        """Callback triggered when graph link is updated."""

    @abc.abstractmethod
    def on_link_deleted(self, link):
        """Callback triggered when graph link is deleted."""
