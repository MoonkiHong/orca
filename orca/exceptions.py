class OrcaError(Exception):

    message = "An unknown exception occurred."

    def __init__(self, **kwargs):
        msg = self.message % kwargs
        super(OrcaError, self).__init__(msg)


class MappingNotFound(OrcaError):

    message = "Mapping not found for key: %(key)s."


class InvalidMappedValue(OrcaError):

    message = "Got invalid value for mapping '%(key)s': %(value)s."
