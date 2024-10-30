class QueueManagementDoesNotExist(Exception):
    ...


class SMSFolderException(Exception):
    ...


class LeadProfileException(Exception):
    ...


class PhoneNumberException(LeadProfileException):
    ...


class TextInputException(LeadProfileException):
    ...


class EmailAddressException(LeadProfileException):
    ...


class CreditCardException(LeadProfileException):
    ...


class FormException(Exception):
    def __init__(self, errors: dict):
        self.errors = errors

    def __str__(self):
        return str(self.errors)


class FieldException(Exception):
    def __init__(self, error: str):
        self.error = error

    def __str__(self):
        return self.error
