from typing import List, Optional, Type, Any, Dict

from langchain_core.pydantic_v1 import BaseModel, Field
from .base import AffiliateBaseTool

from apps.trafficdata.models import Conversion, TrafficData, Lead, Click, Sale
from django.db.models import Sum


class GetStatsSchema(BaseModel):
    range: List[str] = Field(
        ..., description="The date range to get the stats for. for example ['2021-01-01', '2021-01-31']")


class GetStatsTool(AffiliateBaseTool):
    """Tool that returns the stats for an affiliate."""

    name: str = "Get-Stats-Tool"
    description: str = (
        "Use this tool to get the stats for an affiliate within a specific time range."
    )
    args_schema: Type[BaseModel] = GetStatsSchema

    def _run(
        self,
        range: List[str],
        **kwargs,
    ) -> str:
        """Run the tool."""
        # get all the leads and conversions for the affiliate
        # filter by date

        trafficdata = self.affiliate.trafficdata.filter(created_at__range=range)

        # get the total leads and conversions
        clicks = Click.objects.all().count()
        leads = Lead.objects.all().count()
        sales = Sale.objects.all().count()

        # get the total revenue and payout
        return {
            "clicks": clicks,
            "leads": leads,
            "sales": sales,
        }
