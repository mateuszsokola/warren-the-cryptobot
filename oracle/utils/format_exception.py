import json
import sys
import traceback


def format_exception(source_args=None, source_kwargs=None):
    exception_type, exception_value, exception_traceback = sys.exc_info()
    traceback_string = traceback.format_exception(exception_type, exception_value, exception_traceback)
    return json.dumps(
        {
            "errorType": exception_type.__name__,
            "errorMessage": str(exception_value),
            "args": source_args,
            "kwargs": source_kwargs,
            "stackTrace": traceback_string,
        }
    )
