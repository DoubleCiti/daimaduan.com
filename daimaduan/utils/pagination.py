from flask import request


def get_page():
    """ Get current page

    Get current page from query string `page=x`,
    if page not given returns `1` instead.
    """
    try:
        page = request.args.get('page', 1)
        return int(page)
    except ValueError:
        return 1
