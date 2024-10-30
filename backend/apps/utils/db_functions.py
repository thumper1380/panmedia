from django.db.models import Func, FloatField


class ExtractEpoch(Func):
    """
    Custom database function to extract the epoch in milliseconds from a DateTimeField.
    """
    function = 'EXTRACT'
    template = "%(function)s('epoch' from %(expressions)s) * 1000"
    output_field = FloatField()

    def __init__(self, expression):
        super().__init__(expression, output_field=self.output_field)

