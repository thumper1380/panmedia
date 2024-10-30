from django.db.models import Q, F, Count, Case, When, Value, IntegerField
from faker import Faker
from phone_gen import PhoneNumber
import string
import random
from typing import List, Optional, Type, Any, Dict

from langchain_core.pydantic_v1 import BaseModel, Field
from .base import AffiliateBaseTool
from langchain.llms.openai import OpenAI
from django.conf import settings
from langchain.chains import SequentialChain, LLMChain

from langchain.prompts import PromptTemplate
# PydanticOutputParser
from langchain.output_parsers import PydanticOutputParser
from apps.trafficdata.models import TrafficData
from apps.trafficdata.serializers import LeadSerializer
from apps.traffic_distribution.models import Advertiser
from langchain.tools.base import ToolException


# def get_advertiser_field_description():
#     advertisers = Advertiser.objects.all()
#     # list of advertiser names and ids {name: id}
#     advertisers_list = {}
#     for advertiser in advertisers:
#         advertisers_list[advertiser.name] = advertiser.id
#     return (
#         "The advertiser id"
#         + "Here is the list of advertisers in the format of {name: id}:"
#         + str(advertisers_list)
#         + "\n\nif none of the advertisers match, please use None."
#     )


class SendTestLeadSchema(BaseModel):
    """
    Schema for SendTestLeadTool input.

    Attributes:
        country_code: A two-letter ISO country code representing the geographical location. 
                      This code follows the ISO 3166-1 alpha-2 standard. Examples include 'US' for the United States, 
                      'GB' for Great Britain, 'CA' for Canada, and 'AU' for Australia. It is essential to explicitly 
                      request this information if it is not provided, as assumptions or guesses about the country code 
                      are not reliable.

        advertiser_id: A unique identifier for the advertiser. If this ID is not provided, the 'Read-Advertisers-Tool' 
                       should be used to retrieve it. This ID is essential for distinguishing between different advertisers 
                       within the system.
    """
    country_code: str = Field(
        ..., description="A two-letter ISO country code (ISO 3166-1 alpha-2) representing the geographical location. Must be explicitly requested if not provided."
    )

    advertiser_id: int = Field(
        ..., description="A unique identifier for the advertiser. If not provided, use 'Read-Advertisers-Tool' to retrieve it. Essential for distinguishing between different advertisers."
    )


class SendTestLeadTool(AffiliateBaseTool):
    """
    A tool designed to facilitate the testing of lead transmission to affiliates.

    This tool simulates the process of sending a lead to an advertiser, allowing for the verification and 
    validation of the lead transmission process in an affiliate network. It is particularly useful for testing 
    the integration and data flow between affiliate systems and advertisers, ensuring that leads are properly 
    formatted and transmitted according to specified requirements.

    Attributes:
        name: The name of the tool, set to 'Send-Test-Lead'.
        description: A brief explanation of the tool's purpose, which is to enable users to send a simulated 
                     lead to an advertiser for testing and validation purposes.
    """
    name: str = "Send-Test-Lead"
    description: str = "A tool for sending a simulated lead to an advertiser, enabling testing and validation of the lead transmission process in affiliate networks."

    args_schema: Type[SendTestLeadSchema] = SendTestLeadSchema

    def generate_email(self, first_name: str, last_name: str):
        """Generate an email address."""
        first_name = first_name.lower()
        last_name = last_name.lower()
        birth_year = random.randint(1950, 2000)
        random_letters = "".join(random.choices(string.ascii_lowercase, k=2))
        random_numbers = "".join(random.choices(string.digits, k=3))
        email_providers = ["gmail.com", "yahoo.com", "outlook.com"]

        formats = [
            f"{first_name}.{last_name}{random_numbers}@{random.choice(email_providers)}",
            f"{first_name}_{last_name}{random_numbers}@{random.choice(email_providers)}",
            f"{first_name}{last_name}{random_numbers}@{random.choice(email_providers)}",
            f"{first_name[0]}{last_name}{random_numbers}@{random.choice(email_providers)}",
            f"{first_name}.{last_name}_{random_numbers}@{random.choice(email_providers)}",
            f"{first_name}_{last_name}.{random_numbers}@{random.choice(email_providers)}",
            f"{last_name}.{first_name}{random_numbers}@{random.choice(email_providers)}",
            f"{last_name}_{first_name}{random_numbers}@{random.choice(email_providers)}",
            f"{first_name}{last_name}{birth_year}@{random.choice(email_providers)}",
            f"{first_name}{last_name}{random_letters}{random_numbers}@{random.choice(email_providers)}",
            f"{last_name}.{first_name}{random_numbers}@{random.choice(email_providers)}",
            f"{last_name}_{first_name}{random_numbers}@{random.choice(email_providers)}",
            f"{last_name}{first_name}{random_numbers}@{random.choice(email_providers)}"
        ]

        return random.choice(formats)

    @AffiliateBaseTool.handle_errors
    def _run(
        self,
        country_code: str,
        advertiser_id: int,
        **kwargs: Any,
    ) -> str:
        """Run the tool."""
        advertiser_query = Advertiser.objects.filter(id=advertiser_id)

        if not advertiser_query.exists():
            raise ToolException("Advertiser not found.")

        advertiser = advertiser_query.first()

        fake = Faker()

        first_name = fake.first_name()
        last_name = fake.last_name()
        email = self.generate_email(first_name, last_name)
        user_agent = fake.chrome()

        phone_number = PhoneNumber(country_code).get_mobile()
        ipv4 = fake.ipv4()

        # create the lead in the database
        profile = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone_number,
        }

        lead = TrafficData.objects.create(
            ip_address=ipv4,
            affiliate_id=self.affiliate.id,
            country=country_code,
            funnel_id=2,
            user_agent=user_agent,
        )

        # print phone number
        print(f'Phone number: {phone_number}')
        try:
            lead.form_complete(
                description='Lead request from affiliate API', **profile)

            lead.save()

        except Exception as e:
            return str(e), 400

        advertiser_external_id, auto_login_url = advertiser.push_lead(lead)

        lead.advertiser_accepted(
            advertiser_external_id=advertiser_external_id,
            auto_login_url=auto_login_url,
            advertiser_id=advertiser.id,
        )

        lead.save()

        return LeadSerializer(lead).data, 200
