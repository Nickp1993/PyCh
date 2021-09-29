# ==========================================================
# Process decorator
# ==========================================================

def process(func):
    def wrapper(*args, **kwargs):
        """first argument of a process should be env"""
        env = args[0]
        return env.process(func(*args, **kwargs))
    return wrapper
