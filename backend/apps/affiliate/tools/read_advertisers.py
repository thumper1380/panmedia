from langchain.callbacks.manager import CallbackManagerForToolRun
from django.db.models import Q
from typing import List, Optional, Type, Any, Dict

from langchain_core.pydantic_v1 import BaseModel, Field
from .base import AffiliateBaseTool
from apps.traffic_distribution.models import Advertiser
from apps.traffic_distribution.serializers import AdvertiserSerializer


def Response(success: bool = True, data: Any = {}, status: int = 200, error: str = "") -> Dict[str, Any]:
    response = {"success": success, "status": status}
    if success:
        response["data"] = data
    else:
        response["error"] = error
    return response


class ReadAdvertisersSchema(BaseModel):
    """
    Schema for querying advertisers in the system.

    This schema is used to specify the criteria for searching advertisers within the affiliate network. It enables 
    users to search for advertisers using either their unique identifier or name. The flexibility of this schema 
    allows for efficient and targeted retrieval of advertiser information, aiding in various operational and 
    analytical tasks.

    Attributes:
        query: A string used to search for advertisers. This can be either the name or the unique ID of the 
               advertiser. The search is designed to be flexible, accommodating partial matches and varied input formats.
    """
    query: str = Field(
        ..., description="A search string for the advertiser, accepting either the name or unique ID. Designed for flexible and varied input formats."
    )


class ReadAdvertisersTool(AffiliateBaseTool):
    """
    A comprehensive tool for accessing advertiser information in the affiliate network.

    This tool is designed to retrieve detailed information about advertisers. It supports searching by advertiser 
    name or ID, providing a flexible and user-friendly interface for accessing advertiser data. In cases where a 
    specific advertiser is not found, the tool is programmed to return a complete list of all advertisers, ensuring 
    that users have access to broad information when needed. This feature makes it particularly useful for both 
    specific queries and general overviews of advertiser data within the system.

    Attributes:
        name: The name of the tool, set to 'Read-Advertisers-Tool'.
        description: A summary of the tool's functionality, emphasizing its ability to search for advertisers by name 
                     or ID, and its fallback behavior of returning all advertisers if a specific query yields no results.
    """
    name: str = "Read-Advertisers-Tool"
    description: str = (
        "A tool for retrieving advertiser information, supporting searches by name or ID. If a specific advertiser is not found, a complete list of all advertisers is returned."
    )
    args_schema: Type[BaseModel] = ReadAdvertisersSchema

    serializer_class = AdvertiserSerializer

    def _run(
        self,
        query,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs,
    ) -> str:
        """Run the tool."""
        # Generate a lead
        # search by advertsier name or id
        advertisers = Advertiser.objects.filter(
            Q(name__icontains=query) | Q(id__icontains=query))

        if not advertisers.exists():
            advertisers = Advertiser.objects.all()

        advertisers_data = self.serializer_class(advertisers, many=True).data

        return Response(data=advertisers_data)
