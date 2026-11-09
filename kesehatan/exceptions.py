"""P04: exception buatan sendiri (F10)."""


class AbnormalVitalException(Exception):
    def __init__(self, pesan):
        super().__init__(pesan)
