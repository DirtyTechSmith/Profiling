import contextlib
import cProfile
from functools import wraps
import logging

log = logging.getLogger(__name__)


# handler = logging.StreamHandler()
# log.addHandler(handler)
# log.level = logging.INFO


@contextlib.contextmanager
def returnContext():
    """
    Used as an empty context for do_context
    """
    try:
        yield

    finally:
        return


class BaseContext(object):
    is_running = False

    def __new__(cls, *args, **kwargs):
        # default do_context to True, define it in the dict if it is None

        # if  the class is already running, return an empty context
        if cls.is_running:
            return returnContext()

        # define the new class with super
        new_cls = super(BaseContext, cls).__new__(cls, *args, **kwargs)
        # set the class as running prior to the __init__
        cls.is_running = True

        return new_cls


class CProfileContext(BaseContext):
    def __init__(self, profile_header=None, sort=None, subcalls=True, builtins=True, *args, **kwargs):
        """
        create a Cprofile context that will be aware that it is inside itself.
        Args:
            profile_header (str): This string will print out Above the profile
            sort (str):" stdname" , "calls", "time", "cumulative"
            subcalls (bool):
            builtins (bool): i assume will time buildins
            *args (list):
            **kwargs (dict):
        """
        if sort is None:
            sort = 'time'

        if profile_header is not None:
            existing_profile_header = self.__dict__.get('profile_header')
            if existing_profile_header is not None:
                self.profile_header += '\n' + profile_header
            self.profile_header = profile_header

        self.profiler = cProfile.Profile(subcalls=subcalls, builtins=builtins)
        self.sort = sort

    def __enter__(self):
        self.profiler.enable()

    def __exit__(self, type_, value, traceback):
        self.profiler.disable()
        profile_header = self.__dict__.get('profile_header')
        if profile_header is not None:
            print(self.profile_header)

        self.profiler.print_stats(sort=self.sort)


@contextlib.contextmanager
def cProfileContext(profile_header=None, sort=None, do_print=True):
    """
    run code inside a context that will time it
    Args:
        profile_header (str):
        sort (str): sort (str):" stdname" , "calls", "time", "cumulative"
        do_print(bool): sometimes you dont want to print but not retab the code...
    Returns:
    """
    if sort is None:
        sort = 'time'

    profiler = cProfile.Profile()
    profiler.enable()
    try:
        yield

    finally:
        profiler.disable()
        if profile_header is not None:
            print(profile_header)

        if do_print:
            profiler.print_stats(sort=sort)


def cProfileDecorator(func):
    """
    put me in front of your function to get tasty profile timing!
    Examples:
        @cProfileDecorator
        def mySlowFrigginFn():
            for x in range(10000000):
                print('{0}'.format(x))
                print('WHYYYYYYYY')
    Args:
        func ():
    Returns:
    """

    @wraps(func)
    def superFnWrapper(*args, **kwargs):
        with cProfileContext(profile_header=func.__name__):
            func(*args, **kwargs)

    return superFnWrapper
