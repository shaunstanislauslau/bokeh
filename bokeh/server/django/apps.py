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
import os
import glob

# External imports
from django.apps import AppConfig
from django.conf import settings

from tornado.ioloop import IOLoop

# Bokeh imports
from bokeh.command.util import build_single_handler_applications
from bokeh.server.contexts import ApplicationContext
from bokeh.application.handlers.function import FunctionHandler
from bokeh.application.handlers.document_lifecycle import DocumentLifecycleHandler
from .routing import RoutingConfiguration

#-----------------------------------------------------------------------------
# Globals and constants
#-----------------------------------------------------------------------------

__all__ = (
    'DjangoBokehConfig',
)

#-----------------------------------------------------------------------------
# General API
#-----------------------------------------------------------------------------

class DjangoBokehConfig(AppConfig):

    name = label = 'bokeh.server.django'

    def ready(self) -> None:
        if hasattr(settings, "BOKEH_APPS_DIRS"):
            apps_dirs = settings.BOKEH_APPS_DIRS
        else:
            apps_dirs = [os.path.join(settings.BASE_DIR, "bokeh_apps")]

        paths = []
        for apps_dir in apps_dirs:
            paths += [ entry.path for entry in os.scandir(apps_dir) if is_bokeh_app(entry) ]

        apps = build_single_handler_applications(paths)
        for app in apps.values():
            if not any(isinstance(handler, DocumentLifecycleHandler) for handler in app.handlers):
                app.add(DocumentLifecycleHandler())

        # XXX: accessing asyncio's IOLoop directly doesn't work
        io_loop = IOLoop.current()

        contexts = {url: ApplicationContext(app, io_loop=io_loop, url=url) for (url, app) in apps.items()}
        self.routes = RoutingConfiguration(contexts)

#-----------------------------------------------------------------------------
# Dev API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Private API
#-----------------------------------------------------------------------------

def is_bokeh_app(entry: os.DirEntry) -> bool:
    return (entry.is_dir() or entry.name.endswith(('.py', '.ipynb'))) and not entry.name.startswith((".", "_"))

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------
