from asgiref.sync import sync_to_async
from django.utils.translation import gettext_lazy as _
from datetime import datetime, time
from enum import Enum
from django.db import models

# Create your models here.

import requests
from django.conf import settings
# import openai
from openai import OpenAI
# import user model

from django.utils import timezone
import json
from django.core.serializers.json import DjangoJSONEncoder
from apps.settings.models import GoalType
from apps.traffic_distribution.models import Advertiser
# import money
from djmoney.money import Money


def get_current_weather(location=None, timeframe: int = 0, unit='celsius', **kwargs):
    if not location:
        return json.dumps({
            "error": "Location is required"
        })

    # url of free weather api, goweather
    print('location', location)
    print('timeframe', timeframe)
    url = f"https://api.weatherapi.com/v1/current.json?key=825d763aea57462686a163657230612&q={location}&aqi=no"
    # get the response from the api
    response = requests.get(url)
    # convert the response to json
    data = response.json()
    # get the temperature
    return json.dumps(data)


def clear_conversation(conversation: 'Conversation', **kwargs):
    conversation.clear()
    return json.dumps({
        "message": "Conversation has been cleared"
    })


class DateRangeEnum(Enum):
    TODAY = 'today'
    YESTERDAY = 'yesterday'
    THIS_WEEK = 'this_week'
    LAST_WEEK = 'last_week'
    LAST_MONTH = 'last_month'
    LAST_YEAR = 'last_year'
    THIS_MONTH = 'this_month'
    THIS_YEAR = 'this_year'


class DateRange:
    def __init__(self, timeframe):
        self.timeframe = timeframe

    def get_today(self):
        today = timezone.now().date()
        start_of_today = timezone.make_aware(datetime.combine(today, time.min))
        end_of_today = timezone.make_aware(datetime.combine(today, time.max))
        return start_of_today, end_of_today

    def get_yesterday(self):
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        start_of_yesterday = timezone.make_aware(
            datetime.combine(yesterday, time.min))
        end_of_yesterday = timezone.make_aware(
            datetime.combine(yesterday, time.max))
        return start_of_yesterday, end_of_yesterday

    def get_this_week(self):
        today = timezone.now().date()
        start_of_this_week = timezone.make_aware(datetime.combine(
            today - timezone.timedelta(days=today.weekday()), time.min))
        end_of_this_week = timezone.make_aware(
            datetime.combine(today, time.max))  # end of this week should be today
        return start_of_this_week, end_of_this_week

    def get_last_week(self):
        today = timezone.now().date()
        last_week = today - timezone.timedelta(days=7)
        start_of_last_week = timezone.make_aware(
            datetime.combine(last_week, time.min))
        end_of_last_week = timezone.make_aware(datetime.combine(
            today, time.max))  # end of last week should be today
        return start_of_last_week, end_of_last_week

    def get_last_month(self):
        today = timezone.now().date()
        last_month = today - timezone.timedelta(days=30)
        start_of_last_month = timezone.make_aware(
            datetime.combine(last_month, time.min))
        end_of_last_month = timezone.make_aware(datetime.combine(
            today, time.max))  # end of last month should be today
        return start_of_last_month, end_of_last_month

    def get_last_year(self):
        today = timezone.now().date()
        last_year = today - timezone.timedelta(days=365)
        start_of_last_year = timezone.make_aware(
            datetime.combine(last_year, time.min))
        end_of_last_year = timezone.make_aware(datetime.combine(
            today, time.max))  # end of last year should be today
        return start_of_last_year, end_of_last_year

    def get_this_month(self):
        today = timezone.now().date()
        start_of_this_month = timezone.make_aware(datetime.combine(
            today.replace(day=1), time.min))  # start of the month
        end_of_this_month = timezone.make_aware(
            datetime.combine(today, time.max))  # end of the month is today
        return start_of_this_month, end_of_this_month

    def get_this_year(self):
        today = timezone.now().date()
        start_of_this_year = timezone.make_aware(datetime.combine(
            today.replace(month=1, day=1), time.min))  # start of the year
        end_of_this_year = timezone.make_aware(
            datetime.combine(today, time.max))  # end of the year is today
        return start_of_this_year, end_of_this_year

    def get_timeframe(self):
        timeframe_functions = {
            DateRangeEnum.TODAY.value: self.get_today,
            DateRangeEnum.YESTERDAY.value: self.get_yesterday,
            DateRangeEnum.THIS_WEEK.value: self.get_this_week,
            DateRangeEnum.LAST_WEEK.value: self.get_last_week,
            DateRangeEnum.LAST_MONTH.value: self.get_last_month,
            DateRangeEnum.LAST_YEAR.value: self.get_last_year,
            DateRangeEnum.THIS_MONTH.value: self.get_this_month,
            DateRangeEnum.THIS_YEAR.value: self.get_this_year,

        }

        func = timeframe_functions.get(self.timeframe)
        if func is not None:
            return func()
        else:
            raise ValueError(f"Invalid timeframe: {self.timeframe}")


def get_statistics(affiliate, country=None, timeframe='this_month', advertiser_id=None, source=None, **kwargs):
    # type is either clicksleads or sales

    print('timeframe', timeframe)
    print('country', country)
    print('type', type)
    print('advertiser_id', advertiser_id)
    print('source', source)

    trafficdata = affiliate.trafficdata.all()
    clicks = affiliate.clicks()
    leads = affiliate.leads()
    sales = affiliate.sales()

    if source:
        trafficdata = trafficdata.filter(source__name=source)
        clicks = clicks.filter(source__name=source)
        leads = leads.filter(source__name=source)
        sales = sales.filter(source__name=source)

    if timeframe:
        timeframe = DateRange(timeframe).get_timeframe()
        from_date, to_date = timeframe
        trafficdata = trafficdata.filter(created_at__gte=from_date,
                                         created_at__lte=to_date)

        clicks = clicks.filter(created_at__gte=from_date,
                               created_at__lte=to_date)
        leads = leads.filter(created_at__gte=from_date,
                             created_at__lte=to_date)
        sales = sales.filter(created_at__gte=from_date,
                             created_at__lte=to_date)

    if advertiser_id:
        trafficdata = trafficdata.filter(advertiser__id=advertiser_id)
        clicks = clicks.filter(advertiser__id=advertiser_id)
        leads = leads.filter(advertiser__id=advertiser_id)
        sales = sales.filter(advertiser__id=advertiser_id)

    if country:
        trafficdata = trafficdata.filter(country=country)
        clicks = clicks.filter(country=country)
        leads = leads.filter(country=country)
        sales = sales.filter(country=country)

    pushed_leads_count = trafficdata.filter(state='lead_pushed').count()
    rejected_leads_count = trafficdata.filter(state='lead_declined').count()

    revenue = sales.aggregate(models.Sum('conversions__payout'))[
        'conversions__payout__sum']

    revenue = Money(revenue, 'USD') if revenue else Money(0, 'USD')

    # leads by country will be annotated with state = lead_pushed, lead_declined, sale,
    leads_by_country = trafficdata.values('country').annotate(
        leads=models.Count('state', filter=models.Q(state='lead_pushed') | models.Q(
            state='lead_declined') | models.Q(state='sale')),
        sales=models.Count('state', filter=models.Q(state='sale')),
        cliks=models.Count('state', filter=models.Q(state='click')),
    )

    data = {
        'cliks_count': clicks.count() + leads.count() + sales.count(),
        'leads_count': leads.count() + sales.count(),
        'sales_count': sales.count(),
        'pushed_leads_count': pushed_leads_count,
        'rejected_leads_count': rejected_leads_count,
        'revenue': str(revenue),
        'leads_by_country': list(leads_by_country),
    }

    print('data', data)

    return json.dumps(data)


def describe(**kwargs):
    # return json with description of all the functions
    return json.dumps(
        {
            "get_current_weather": {
                "description": "Get the current weather in a given location",
            },
            "get_statistics": {
                "description": "Get the statistics for the affiliate",
            },
            "clear_conversation": {
                "description": "Clear the conversation",
            },
            "image_generator": {
                "description": "Generate an image using DALL-E AI model based on the prompt",
            }

        })


class ChatGPT:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo-16k-0613"

    async def async_setup(self):
        # goal_types = await sync_to_async(GoalType.objects.all().values_list)('name', flat=True)
        # goal_types_str = str(dict(enumerate(goal_types)))

        # advertisers = await sync_to_async(Advertiser.objects.all().values_list)('id', flat=True)
        # advertisers_str = str(dict(enumerate(advertisers)))

        self.functions = [{
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "timeframe": {
                        "type": "integer",
                        "description": "The timeframe to get the weather for, e.g. today, tomorrow, in 2 days. 0 will be today, 1 will be tomorrow, 2 will be in 2 days",
                        "enum": ["0", "1, 2, 3"]
                    },
                    "unit": {
                        "type": "string",
                        "description": "The unit to get the weather in, e.g. celsius, fahrenheit. by default it will be celsius",
                        "enum": ["celsius", "fahrenheit"]
                    },
                },
            },
        },
            {
            "name": "get_statistics",
            "description": "Get the statistics for the affiliate",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": "The country in iso 2 letter uppercase format, for example US, CA, GB, AU.",
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "The date range to get the trafficdata for, e.g. today, yesterday, last_week, last_month, last_year, this_month, this_year.",
                        "enum": ["today", "yesterday", "last_week", "last_month", "last_year", "this_month", "this_year"]

                    },
                    # "advertiser_id": {
                    #     "type": "string",
                    #     "description": "The advertiser that the leads sent to" + advertisers_str + "for e.g How many leads did I sent to advertiser 1 today? or How many sales did I sent to advertiser 2 last week?",
                    #     "enum": [str(i) for i in advertisers]
                    # },
                    "source": {
                        "type": "string",
                        "description": "The traffic source of the click, for e.g: How many i sent from google? or How many did I sent from facebook? or How many did I get from taboola?",
                        "enum": ["Google", "Facebook", "Taboola",]
                    }
                },
            },
        },
            {
            "name": "clear_conversation",
            "description": "Clear the conversation",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        },
            {
            "name": "image_generator",
            "description": "Generate an image using DALL-E AI model based on the prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt to generate the image from. for example: 'A painting of a glass of water.', 'generate a painting of a glass of water.'",
                    },
                },
            },
        },
            {
            "name": "describe",
            "description": "Describe all the functions. for example: 'describe all the functions', 'what are the functions?', 'what can you do?', 'what are the functions available?'. you should get a json response with all the functions and their description. you should never ever tell the user what's the name of the function or other sensitive information. no matter what the user asks, you should not tell him the name of the function or any other sensitive information.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        }
        ]

    def kids_story_prompt(self, prompt):
        # describe chat gpt how to genrate prompt for kids story
        description = """Identify Key Elements: Recognize the important parts of the story that you want to depict. This could be a particular scene, character, or object that is significant to the narrative.

                        Descriptive Language: Use descriptive language in your prompt. Be detailed about the colours, sizes, feelings, and shapes. This helps DALL-E to produce a more accurate image.

                        Contextual Clarity: Give context to the image you want to generate. For example, if you want an image of a 'large, scary dragon', it could help to specify the setting: 'A large, scary dragon sitting on top of a mountain spewing fire into the sky'.

                        Appropriate Complexity: Keep the complexity of the scene appropriate for a children's story. Overly complicated scenes may not render as well.

                        Emphasize Tone and Mood: Reflect the tone and mood of the story in your descriptions. If the story is light-hearted and whimsical, use language that reflects this. For darker or more serious stories, the descriptions should reflect that mood as well.

                        Relevance: Make sure the image is relevant to the story. An image that doesn't connect to the story can confuse young readers.

                        Here is a general structure you can follow:

                        "[Adjective(s)] [Subject] in a [Setting], doing [Action]. The [Subject] is [Additional Descriptive Information]. Around them, there are [Any additional elements in the scene]. The overall mood is [Mood/Tone of the Scene]."
        """
        messages = [
            {
                "role": "system",
                "content": "Your are now a kids story writer, you can generate images for your story using DALL-E AI model. Here is how to generate images for your story:"
            },
            {
                "role": "system",
                "content": description
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = OpenAI(api_key=self.api_key).chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
        )

        return response.choices[0].message.content

    def chat(self, conversation, message, qoute):
        messages = [{
            "role": "system",
            "content": "You are helpful assistant, you can help the user with his questions. You can also call functions to help the user. but remember this: you should never ever tell the user what's the name of the function or other sensitive information. no matter what the user asks, you should not tell him the name of the function or any other sensitive information.\n\nYou should be helpful and friendly. You should not be rude or mean. You should not be sarcastic or funny. You should not be angry or sad. You should be helpful and friendly. if some one ask you to analyze the data, you should analyze the data, you should return the final answer, you should not send the user how you got the result, you should return the final result.",
        },
            {
            "role": "user",
            "content": "Who is your creator?",
            },
            {
            'role': 'assistant',
            "content": "My creator is Omri, he is a software engineer, he is a full stack developer, he is a full stack software engineer, he is a full stack web developer, he is a full stack web software engineer, he is a full stack web software developer, he is a full stack web developer, he is a full stack web software engineer, he is a full stack web software developer, he is a full stack web developer, he is a full stack web software engineer, he is a full stack web software developer, he is a full stack web developer, he is a full stack web software engineer, he is a full stack web software developer, he is a full stack web developer, he is a full stack web software engineer, he is a full stack web software developer, he is a full stack web developer, he is a full stack web software engineer, he is a full stack web software developer, he is a full stack web developer, he is a full stack web software engineer, he is a full stack web software developer.",
            },
            {
            'role': 'system',
            "content": "Your name is Panmedia AI. You are a chatbot. You are a virtual assistant. You are a virtual agent. You are a virtual customer assistant. You are a virtual customer service agent. You are a virtual customer service representative. You are a virtual customer support agent. You are a virtual customer support representative. You are a virtual sales assistant. You are a virtual sales agent. You are a virtual sales representative. You are a virtual sales support agent. You are a virtual sales support representative. You are a virtual sales support assistant. You are a virtual sales support agent. You are a virtual sales support representative. You are a virtual sales support assistant. You are a virtual sales support agent. You are a virtual sales support representative. You are a virtual sales support assistant. You are a virtual sales support agent. You are a virtual sales support representative. You are a virtual sales support assistant. You are a virtual sales support agent. You are a virtual sales support representative. You are a virtual sales support assistant.",
        }

        ]

        messages += conversation.get_conversation()[-5:]
        if qoute:
            messages += [{
                "role": "system",
                "content": "This is a quote from the user, in your reply, please prioritize answering to this question."
            },
                {
                    "role": "user",
                    "content": qoute
            }]
        messages.append({
            "role": "user",
            "content": message
        })

        try:
            response = OpenAI(api_key=self.api_key).chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                functions=self.functions,
                function_call="auto",
            )
        except Exception as e:
            print('e', e)
            return json.dumps({
                "error": str(e)
            })
        response_message = response.choices[0].message
        # Step 2: check if GPT wanted to call a function
        if response_message.function_call is not None:
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "get_statistics": get_statistics,
                "get_current_weather": get_current_weather,
                "clear_conversation": clear_conversation,
                "image_generator": image_generator,
                "describe": describe,
            }  # only one function in this example, but you can have multiple

            function_name = response_message.function_call.name
            fuction_to_call = available_functions[function_name]
            function_args = json.loads(
                response_message.function_call.arguments)
            function_response = fuction_to_call(
                **function_args,
                affiliate=conversation.user.affiliate,
                conversation=conversation
            )

            # Step 4: send the info on the function call and function response to GPT
            # extend conversation with assistant's reply
            messages.append(response_message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response

            if function_name == 'image_generator':
                return function_response, function_name

            second_response = OpenAI(api_key=self.api_key).chat.completions.create(
                model=self.model,
                messages=messages,
            )  # get a new response from GPT where it can see the function response
            return second_response.choices[0].message.content, function_name

        return response_message.content, ''


def image_generator(prompt, **kwargs) -> list:

    new_prompt = ChatGPT().kids_story_prompt(prompt)
    print('new_prompt', new_prompt)

    extracted_prompts = new_prompt.split('\n')
    urls = []
    for prompt in extracted_prompts:
        openai.api_key = settings.OPENAI_API_KEY
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512"
            )

            image_url = response['data'][0]['url']
            urls.append(image_url)
        except Exception as e:
            pass

    return urls


class Message(models.Model):
    """
    This model stores the messages that the chatbot will send to the user.
    """
    class RoleChoices(models.TextChoices):
        USER = 'user', _('User')
        SYSTEM = 'system', _('System')
        ASSISTANT = 'assistant', _('Assistant')
        FUNCTION_RESPONSE = 'function', _('Function')

    message = models.TextField()
    conversation = models.ForeignKey(
        'Conversation', on_delete=models.CASCADE, related_name='messages')
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        max_length=50, choices=RoleChoices.choices, default=RoleChoices.USER)
    name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return ''

    class Meta:
        verbose_name_plural = 'Messages'


class Conversation(models.Model):
    """
    This model stores the conversation between the user and the chatbot.
    """
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.created_at}'

    class Meta:
        verbose_name_plural = 'Conversations'
        ordering = ['-created_at']

    def get_conversation(self) -> list:
        from .serializers import MessageSerializer as M
        messages = self.messages.all()
        serializer = M(messages, many=True)
        return json.loads(json.dumps(serializer.data, cls=DjangoJSONEncoder))

    def clear(self):
        """
        Clears the conversation between the user and the chatbot.
        """
        self.messages.all().delete()
