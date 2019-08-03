import cProfile
from contextlib import contextmanager


@contextmanager
def cprofileContext(profile_header=None, do_context=True):
    """

    Args:
        profile_header (str):
        do_context (bool):

    Returns:

    """
    if not do_context:
        yield
        return

    the_profiler = cProfile.Profile()
    the_profiler.enable()
    try:
        yield

    finally:
        the_profiler.disable()
        if profile_header:
            print(profile_header)

        the_profiler.print_stats()
