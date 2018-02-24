# Based on Django's approach -> http://code.djangoproject.com/svn/django/trunk/django/__init__.py
VERSION = (1, 12, 0, 'final')

def get_version(version=None):
    """Derives a PEP386-compliant version number from VERSION.
       Simplified from http://code.djangoproject.com/svn/django/trunk/django/__init__.py
    """
    if version is None:
        version = VERSION

    parts = len(version) -1
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    if version[3] != 'final':
        sub = '-' + str(version[3])

    return main + sub
