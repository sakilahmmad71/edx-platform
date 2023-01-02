"""API utils"""

import logging
import requests
from algoliasearch.exceptions import RequestException, AlgoliaUnreachableHostException
from django.conf import settings

from lms.djangoapps.utils import AlgoliaClient

log = logging.getLogger(__name__)

COURSE_LEVELS = [
    'Introductory',
    'Intermediate',
    'Advanced'
]


def get_personalized_course_recommendations(user_id):
    """ Get personalize recommendations from Amplitude. """
    headers = {
        'Authorization': f'Api-Key {settings.AMPLITUDE_API_KEY}',
        'Content-Type': 'application/json'
    }
    params = {
        'user_id': user_id,
        'get_recs': True,
        'rec_id': settings.REC_ID,
    }
    try:
        response = requests.get(settings.AMPLITUDE_URL, params=params, headers=headers)
        if response.status_code == 200:
            response = response.json()
            recommendations = response.get('userData', {}).get('recommendations', [])
            if recommendations:
                is_control = recommendations[0].get('is_control')
                has_is_control = recommendations[0].get('has_is_control')
                recommended_course_keys = recommendations[0].get('items')
                return is_control, has_is_control, recommended_course_keys
    except Exception as ex:  # pylint: disable=broad-except
        log.warning(f'Cannot get recommendations from Amplitude: {ex}')

    return True, False, []


def get_algolia_courses_recommendation(course_data):
    """ Get personalized courses recommendation from Algolia search. """
    algolia_client = AlgoliaClient.get_algolia_client()
    algolia_index = algolia_client.init_index(settings.ALGOLIA_COURSES_RECOMMENDATION_INDEX_NAME)

    search_query = course_data["skill_names"]
    searchable_course_levels = [
        f"level:{course_level}"
        for course_level in COURSE_LEVELS
        if course_level.lower() != course_data["level_type"].lower()
    ]
    if algolia_client:
        try:
            # Algolia search filter criteria:
            # - Product type: Course
            # - Courses are available (enrollable)
            # - Courses should not have the same course level as the current course
            # - Exclude current course from the results
            results = algolia_index.search(
                search_query,
                {
                    "filters": f"NOT active_run_key:'{course_data['key']}'",
                    "facetFilters": ["availability:Available now", "product:Course", searchable_course_levels],
                    "optionalWords": f"{search_query}",
                }
            )

            return results
        except (AlgoliaUnreachableHostException, RequestException) as ex:
            log.warning(f"Unexpected exception while attempting to fetch courses data from Algolia: {str(ex)}")

    return {}
