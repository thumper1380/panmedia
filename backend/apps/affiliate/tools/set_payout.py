from typing import List, Optional, Type, Any, Dict

from langchain_core.pydantic_v1 import BaseModel, Field
from .base import AffiliateBaseTool

from apps.leads_conversions.models import PayoutAffiliateFolder, PayoutCountryFolder, PayoutFolder


class SetPayoutSchema(BaseModel):
    """Input for SetPayoutTool."""

    # advertiser: str = Field(None, description="The advertiser name or id",)

    value: float = Field(
        ...,
        description="The value of the payout.",
    )

    country: str = Field(
        None,
        description="2 letter country code, for example US, IL, GB, etc.",
    )



class SetPayoutTool(AffiliateBaseTool):
    """Tool that sets a payout for an affiliate."""

    name: str = "Set-Payout-Tool"
    description: str = (
        "Use this tool to set a payout for an affiliate for specific country."
    )
    args_schema: Type[BaseModel] = SetPayoutSchema

    def _run(
        self,
        value: float,
        country: str,
        **kwargs,
    ) -> str:
        """Run the tool."""
        

        country_folder = PayoutCountryFolder.objects.create(name=country)

        payout_folder = PayoutFolder.objects.create(name="P", value=value) 

        affiliate_folder = PayoutAffiliateFolder.objects.create(name=self.affiliate.name, affiliate=self.affiliate)

        # each folder has a parent lets define it COUNTRY>>AFFILIATE>>PAYOUT

        payout_folder.parent = affiliate_folder
        payout_folder.save()

        affiliate_folder.parent = country_folder
        affiliate_folder.save()

        
        return f"Set payout for {self.affiliate.name} to {value} for {country}."
    


