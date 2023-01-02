"""
Helper Methods
"""

from algoliasearch.search_client import SearchClient
from braze.client import BrazeClient
from django.conf import settings
from optimizely import optimizely
from optimizely.config_manager import PollingConfigManager


def _get_key(key_or_id, key_cls):
    """
    Helper method to get a course/usage key either from a string or a key_cls,
    where the key_cls (CourseKey or UsageKey) will simply be returned.
    """
    return (
        key_cls.from_string(key_or_id)
        if isinstance(key_or_id, str)
        else key_or_id
    )


def get_braze_client():
    """ Returns a Braze client. """
    braze_api_key = settings.EDX_BRAZE_API_KEY
    braze_api_url = settings.EDX_BRAZE_API_SERVER

    if not braze_api_key or not braze_api_url:
        return None

    return BrazeClient(
        api_key=braze_api_key,
        api_url=braze_api_url,
        app_id='',
    )


class OptimizelyClient:
    """ Class for instantiating an Optimizely full stack client instance. """
    optimizely_client = None

    @classmethod
    def get_optimizely_client(cls):
        if not cls.optimizely_client:
            optimizely_sdk_key = settings.OPTIMIZELY_FULLSTACK_SDK_KEY
            if not optimizely_sdk_key:
                return None

            config_manager = PollingConfigManager(
                update_interval=10,
                sdk_key=optimizely_sdk_key,
            )
            cls.optimizely_client = optimizely.Optimizely(config_manager=config_manager)

        return cls.optimizely_client


class AlgoliaClient:
    """ Class for instantiating an Algolia search client instance. """
    algolia_client = None
    algolia_app_id = settings.ALGOLIA_APP_ID
    algolia_search_api_key = settings.ALGOLIA_SEARCH_API_KEY

    @classmethod
    def get_algolia_client(cls):
        if not cls.algolia_client:
            if not (cls.algolia_app_id and cls.algolia_search_api_key):
                return None

            cls.algolia_client = SearchClient.create(cls.algolia_app_id, cls.algolia_search_api_key)

        return cls.algolia_client
