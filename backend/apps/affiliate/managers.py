from django.db import models




class TelegramProfileQuerySet(models.QuerySet):
    def get_by_chat_id(self, chat_id):
        return self.get(chat_id=chat_id)



class AffiliateQuerySet(models.QuerySet):
    ...

class PostbackQuerySet(models.QuerySet):
    def fire(self, goal, lead):
        postbacks = self.filter(goal=goal, active=True)
        for postback in postbacks:
            postback.fire(lead)

    def pending(self, goal, lead):
        postbacks = self.filter(goal=goal, active=True)
        for postback in postbacks:
            postback.pending(postback, lead)

class EventNotificationQuerySet(models.QuerySet):
    def notify(self, state, **kwargs):
        events = self.filter(state=state)
        for event in events:
            event.notify(**kwargs)
