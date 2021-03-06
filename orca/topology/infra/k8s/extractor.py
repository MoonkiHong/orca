import abc

from orca.graph import graph
from orca.topology import extractor


class Extractor(extractor.Extractor):

    def get_origin(self):
        return 'kubernetes'

    def extract(self, entity):
        node_id = self._extract_id(entity)
        properties = self._extract_properties(entity)
        return graph.Node(node_id, properties, self.get_origin(), self.get_kind())

    def _extract_id(self, entity):
        return entity.metadata.uid

    @abc.abstractmethod
    def _extract_properties(self, entity):
        """Extracts properties from given K8S object."""
