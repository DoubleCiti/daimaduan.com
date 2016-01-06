def get_session(request):
    """Get session instance from request"""

    return request.environ.get('beaker.session')
