class {{ project_name | capitalize }}Error(Exception):
    """Base exception for {{ project_name }}."""
    pass


class ConfigurationError({{ project_name | capitalize }}Error):
    """Raised when there is a configuration error."""
    pass


class ResourceNotFoundError({{ project_name | capitalize }}Error):
    """Raised when a required resource is not found."""
    pass
