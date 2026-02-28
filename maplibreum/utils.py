import itertools

class IDGenerator:
    _counters = {}

    @classmethod
    def reset(cls):
        """Reset all counters. Useful between tests or example generation."""
        cls._counters.clear()

    @classmethod
    def get_id(cls, prefix=""):
        """Get a unique ID with the given prefix using an incrementing counter."""
        if prefix not in cls._counters:
            cls._counters[prefix] = itertools.count()
        return f"{prefix}{next(cls._counters[prefix])}"

def get_id(prefix=""):
    return IDGenerator.get_id(prefix)
