import logging
import math

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def get_trending_places(places):
    """Return places ranked by cached YouTube engagement, with a safe fallback."""
    fallback = [dict(place) for place in places]
    if not settings.YOUTUBE_API_KEY:
        return _with_source(fallback, "curated")

    cache_key = "wildwolves:youtube:trending:v1"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        enriched = [_youtube_metrics(place) for place in places]
    except requests.RequestException as exc:
        logger.warning("YouTube recommendation request failed: %s", exc)
        return _with_source(fallback, "curated")
    except (KeyError, TypeError, ValueError) as exc:
        logger.warning("YouTube recommendation response was invalid: %s", exc)
        return _with_source(fallback, "curated")

    ranked = _rank(enriched)
    result = _with_source(ranked, "youtube")
    cache.set(cache_key, result, settings.YOUTUBE_RECOMMENDATION_CACHE_SECONDS)
    return result


def _youtube_metrics(place):
    params = {
        "key": settings.YOUTUBE_API_KEY,
        "part": "snippet",
        "q": f"{place['name']} Manipur tourism",
        "type": "video",
        "order": "relevance",
        "maxResults": 5,
    }
    response = requests.get(SEARCH_URL, params=params, timeout=8)
    response.raise_for_status()
    search_data = response.json()
    video_ids = [
        item["id"]["videoId"]
        for item in search_data.get("items", [])
        if item.get("id", {}).get("videoId")
    ]

    metrics = dict(place)
    metrics.update({
        "video_count": len(video_ids),
        "total_views": 0,
        "total_likes": 0,
        "total_comments": 0,
    })
    if not video_ids:
        return metrics

    stats_response = requests.get(
        VIDEOS_URL,
        params={
            "key": settings.YOUTUBE_API_KEY,
            "part": "statistics,snippet",
            "id": ",".join(video_ids),
        },
        timeout=8,
    )
    stats_response.raise_for_status()
    stats_data = stats_response.json()
    for item in stats_data.get("items", []):
        statistics = item.get("statistics", {})
        metrics["total_views"] += int(statistics.get("viewCount", 0))
        metrics["total_likes"] += int(statistics.get("likeCount", 0))
        metrics["total_comments"] += int(statistics.get("commentCount", 0))

    if stats_data.get("items"):
        thumbnail = stats_data["items"][0].get("snippet", {}).get("thumbnails", {})
        metrics["image"] = (
            thumbnail.get("high", {}).get("url")
            or thumbnail.get("medium", {}).get("url")
            or place["image"]
        )
    return metrics


def _rank(places):
    raw_scores = [
        math.log10(
            1
            + place["total_views"]
            + (place["total_likes"] * 10)
            + (place["total_comments"] * 3)
        )
        for place in places
    ]
    maximum = max(raw_scores, default=0) or 1
    for place, raw_score in zip(places, raw_scores):
        place["score"] = round((raw_score / maximum) * 100)
    return sorted(places, key=lambda place: (place["score"], place["total_views"]), reverse=True)


def _with_source(places, source):
    for place in places:
        place["recommendation_source"] = source
    return places
