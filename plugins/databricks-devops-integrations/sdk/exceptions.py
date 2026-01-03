"""
Custom exceptions for DevOps Integration plugins
"""


class PluginError(Exception):
    """Base exception for all plugin errors"""

    pass


class AuthenticationError(PluginError):
    """Raised when authentication with the DevOps platform fails"""

    pass


class ConfigurationError(PluginError):
    """Raised when plugin configuration is invalid"""

    pass


class WorkItemNotFoundError(PluginError):
    """Raised when a work item cannot be found"""

    pass


class IntegrationError(PluginError):
    """Raised when integration with external system fails"""

    pass


class RateLimitError(PluginError):
    """Raised when API rate limit is exceeded"""

    pass


class PermissionError(PluginError):
    """Raised when user lacks necessary permissions"""

    pass


class ValidationError(PluginError):
    """Raised when input validation fails"""

    pass
