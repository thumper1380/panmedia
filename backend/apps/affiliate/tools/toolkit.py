from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.agents.tools import BaseTool
from apps.affiliate.models import Affiliate
from typing import Any, Dict, Optional, Type, List
from .send_test_lead import SendTestLeadTool
from .set_payout import SetPayoutTool
from .get_stats import GetStatsTool
from langchain.callbacks.base import BaseCallbackHandler

from .read_advertisers import ReadAdvertisersTool
from langchain.utilities.dalle_image_generator import DallEAPIWrapper
from langchain.tools.base import ToolException



from langchain.memory import PostgresChatMessageHistory



class AffiliateToolKit(BaseToolkit):
    """Toolkit for interacting with Affiliate."""

    affiliate: Affiliate
    callbacks: Optional[List[BaseCallbackHandler]] = None

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        # Implement the logic to retrieve the tools available in the toolkit
        # GetStats
        # SendTestLead
        #
        return [
            ReadAdvertisersTool(affiliate=self.affiliate,
                                callbacks=self.callbacks),
            SendTestLeadTool(affiliate=self.affiliate,
                             callbacks=self.callbacks),
            SetPayoutTool(affiliate=self.affiliate, callbacks=self.callbacks),
            GetStatsTool(affiliate=self.affiliate, callbacks=self.callbacks),
        ]
