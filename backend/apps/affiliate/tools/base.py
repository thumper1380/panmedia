from functools import wraps
from typing import Any, Dict, Optional, Type, List, Callable
from langchain_core.pydantic_v1 import Field
from apps.affiliate.models import Affiliate
from langchain.tools.base import BaseTool
from langchain.tools.base import ToolException


def handle_tool_exception(error: ToolException) -> Dict[str, Any]:
    """Handle a tool exception."""
    return (
        "An error occurred while running the tool. Please try again later."
        + error.args[0]
        + "Please try another tool."
    )


class AffiliateBaseTool(BaseTool):
    """Base class for affiliate tools."""

    affiliate: Affiliate
    handle_tool_error: Optional[Callable[[
        ToolException], Dict[str, Any]]] = handle_tool_exception

    @staticmethod
    def handle_errors(func):
        """Decorator for handling errors in tool methods."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise ToolException(str(e))
        return wrapper
