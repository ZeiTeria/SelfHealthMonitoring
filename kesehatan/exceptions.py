class AbnormalVitalException(Exception):
    def __init__(self, pesan):
        super().__init__(pesan)
