#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2019, Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Boilerplate
#-----------------------------------------------------------------------------
from __future__ import absolute_import, division, print_function, unicode_literals

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
import re
from typing import Dict, List

# External imports
from django.conf.urls import url
from django.urls.resolvers import URLPattern
from channels.http import AsgiHandler

# Bokeh imports
from bokeh.server.contexts import ApplicationContext
from .consumers import BokehAppHTTPConsumer, BokehAppWebsocketConsumer

#-----------------------------------------------------------------------------
# Globals and constants
#-----------------------------------------------------------------------------

__all__ = (
    'RoutingConfiguration',
)

#-----------------------------------------------------------------------------
# General API
#-----------------------------------------------------------------------------

class RoutingConfiguration(object):

    _http_urlpatterns = []
    _websocket_urlpatterns = []

    _prefix = "bokehapps"

    def __init__(self, app_contexts: Dict[str, ApplicationContext]):

        for app_name, app_context in app_contexts.items():
            self._add_new_routing(app_name, app_context)

    def get_http_urlpatterns(self) -> List[URLPattern]:
        return self._http_urlpatterns + [url(r"", AsgiHandler)]

    def get_websocket_urlpatterns(self) -> List[URLPattern]:
        return self._websocket_urlpatterns

    def _add_new_routing(self, app_name: str, app_context: ApplicationContext) -> None:
        kwargs = dict(app_context=app_context)

        def urlpattern(suffix=""):
            prefix = self._prefix + "/" if self._prefix else ""
            return r"^{}{}{}$".format(prefix, re.escape(app_name), suffix)

        self._http_urlpatterns.append(url(urlpattern(), BokehAppHTTPConsumer, kwargs=kwargs))
        self._websocket_urlpatterns.append(url(urlpattern("/ws"), BokehAppWebsocketConsumer, kwargs=kwargs))

#-----------------------------------------------------------------------------
# Dev API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Private API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------
