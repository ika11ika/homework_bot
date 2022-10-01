class BotSendMessageException(Exception):
    """Telegram bot send message exception."""

    def __init__(self, *args):
        """Init method."""
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        """Create full error string."""
        if self.message:
            return f'BotSendMessageException, {self.message}'
        return 'BotSendMessageException has been raised'


class GetAPIAnswerException(Exception):
    """Telegram bot send message exception."""

    def __init__(self, *args):
        """Init method."""
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        """Create full error string."""
        if self.message:
            return f'GetAPIAnswerException, {self.message}'
        return 'GetAPIAnswerException has been raised'


class APIFormatResponseException(Exception):
    """API response format exception."""

    def __init__(self, *args):
        """Init method."""
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        """Create full error string."""
        if self.message:
            return f'APIResponseException, {self.message}'
        return 'APIResponseException has been raised'


class EmptyResponseExeption(Exception):
    """Empty API response format exception."""

    def __init__(self, *args):
        """Init method."""
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        """Create full error string."""
        if self.message:
            return f'EmptyResponseExeption, {self.message}'
        return 'EmptyResponseExeption has been raised'
