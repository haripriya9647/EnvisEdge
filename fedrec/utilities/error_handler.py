from functools import wraps
import tracemalloc


def errorhandler(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()

        try:
            return func(*args, **kwargs)

        
        except NotImplementedError as ner:
            print("NotImplementedError: ", ner)
        except OSError as osr:
            print("OSError: ", osr)
        except ReferenceError as rfe:
            print("Reference Error: ", rfe)
        # Implement different Error/Exceptions as required.

        except Exception as e:
            print("Exception: ", e)
        
        tracemalloc.stop()
    
    return wrapper

"""
    Can be extended further as required.
"""
