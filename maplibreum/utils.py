class IDGenerator:
    _counters = {}

    @classmethod
    def get_id(cls, prefix=""):
        if prefix not in cls._counters:
            cls._counters[prefix] = 0
        current_id = f"{prefix}{cls._counters[prefix]}"
        cls._counters[prefix] += 1
        return current_id

    @classmethod
    def reset(cls):
        cls._counters = {}

def get_id(prefix=""):
    return IDGenerator.get_id(prefix)
