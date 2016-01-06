import math

from bottle import request


def paginate(collection, current_page, per_page=20):
    total_page = int(math.ceil((float(collection.count()) / per_page)))

    start_index = (current_page - 1) * per_page
    end_index = current_page * per_page
    page_collection = collection[start_index:end_index]

    summary = {'total_page': total_page,
               'current_page': current_page,
               'previous_page': current_page - 1,
               'next_page': current_page + 1,
               'is_first_page': current_page == 1,
               'is_last_page': current_page == total_page}

    return page_collection, summary


def get_page():
    """ Get current page

    Get current page from query string `page=x`,
    if page not given returns `1` instead.
    """
    try:
        page = request.params.get('page', 1)
        return int(page)
    except ValueError:
        return 1
