from datetime import datetime
import pytz

class PhnomPenhTime:
    TZ = pytz.timezone("Asia/Phnom_Penh")

    @classmethod
    def now(cls):
        """Return current Phnom Penh datetime"""
        return datetime.now(cls.TZ)
