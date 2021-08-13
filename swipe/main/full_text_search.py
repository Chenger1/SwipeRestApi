from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


def get_queryset(queryset, query):
    search_query = SearchQuery(query)
    search_vector = SearchVector('house__city', weight='A')
    results = queryset.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
    return results
