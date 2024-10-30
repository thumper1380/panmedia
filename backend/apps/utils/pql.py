from pyparsing import (
    Word, alphas, alphanums, nums, Literal, delimitedList,
    infixNotation, opAssoc, QuotedString, oneOf, Group,
    ParserElement, CaselessLiteral
)
from django.db.models import Q

ParserElement.enablePackrat()

class PQL:
    def __init__(self):
        # Define basic elements
        identifier = Word(alphas + "_", alphanums + "_")
        number = Word(nums).setParseAction(lambda t: int(t[0]))  # Convert numbers to integers

        # QuotedString helps to get string tokens in quotes
        quoted_string = QuotedString("'", escChar='\\', unquoteResults=True)
        value = number | quoted_string

        # Define a list of values
        list_of_values = Literal('[') + delimitedList(value) + Literal(']')

        # Define operators
        operator = oneOf("IN NOT_IN > < =")

        # Define condition as a combination of identifier, operator and value or list of values
        condition = Group(identifier + operator + (list_of_values | value))

        # Define logical operators
        and_ = CaselessLiteral("AND")
        or_ = CaselessLiteral("OR")

        # Use infixNotation to handle operator precedence & associativity
        self.query_parser = infixNotation(condition, [(and_, 2, opAssoc.LEFT), (or_, 2, opAssoc.LEFT)])

    def parse_query(self, input_string):
        return self.query_parser.parseString(input_string, parseAll=True)

    def parse_to_query(self, parsed_conditions):
        filters = Q()

        for condition in parsed_conditions:
            if isinstance(condition, str):
                if condition == 'AND':
                    continue  # For 'AND', we just chain the conditions which is the default behavior of Q()
                elif condition == 'OR':
                    raise NotImplementedError("OR conditions are not implemented in this example")
            else:
                condition = condition.asList()
                field, operator, values = condition[0], condition[1], condition[2:]

                # If value is a list, get the inner elements
                if isinstance(values[0], list):
                    values = values[0]

                if operator == 'IN':
                    filters &= Q(**{f'{field}__in': values})
                elif operator == 'NOT_IN':
                    filters &= ~Q(**{f'{field}__in': values})
                elif operator == '>':
                    filters &= Q(**{f'{field}__gt': values[0]})
                elif operator == '<':
                    filters &= Q(**{f'{field}__lt': values[0]})
                elif operator == '=':
                    filters &= Q(**{f'{field}': values[0]})
                else:
                    raise ValueError(f"Invalid operator: {operator}")

        return filters


