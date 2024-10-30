import datetime
from rest_framework.exceptions import ValidationError
from django.utils import timezone


class DateValidationMixin:

    def validate_dates(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date is None or end_date is None:
            raise ValidationError({'error': 'Missing dates'})

        try:
            start = datetime.datetime.combine(
                datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                datetime.time.min)

            end = datetime.datetime.combine(
                datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                datetime.time.max)

            # check if end date is greater than today
            # if end.date() > timezone.now().date():
            #     # set the end date to today
            #     end = datetime.datetime.combine(
            #         timezone.now(),
            #         datetime.time.max)

            request.start_date = start
            request.end_date = end
        except ValueError:
            raise ValidationError({"error": "Invalid date format"})

        return True
