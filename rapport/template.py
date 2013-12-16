# Copyright 2013 Sascha Peilicke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import os
import re
import sys

import jinja2
import json

from rapport.config import USER_CONFIG_DIR

def _get_template_dirs(type="plugin"):
    """Return a list of directories where templates may be located.
    """
    template_dirs = [
        os.path.expanduser(os.path.join(USER_CONFIG_DIR, "templates", type)),
        os.path.join("rapport", "templates", type)  # Local dev tree
    ]
    return template_dirs


_JINJA2_ENV = {}

def sub_filter(s, find, replace):
    """A non-optimal implementation of a regex filter"""
    return re.sub(find, replace, s)

def subn_filter(s, find, replace, count=0):
    """A non-optimal implementation of a regex filter"""
    return re.gsub(find, replace, count, s)

def firstline_filter(s):
    return re.sub("\n.*", '', s)

# useful for debugging when authoring templates
def json_filter(val):
    return json.dumps(val, sort_keys=True, indent=4)

def init():
    for type in ["plugin", "email", "web"]:
        loader = jinja2.FileSystemLoader(_get_template_dirs(type))
        env = jinja2.Environment(loader=loader,
                                 extensions=["jinja2.ext.i18n", "jinja2.ext.loopcontrols"],
                                 line_statement_prefix="%%",
                                 line_comment_prefix="##",
                                 trim_blocks=True)
        env.install_null_translations(newstyle=False)
        env.filters['firstline'] = firstline_filter
        env.filters['json']      = json_filter
        env.filters['sub']       = sub_filter
        env.filters['subn']      = subn_filter
        _JINJA2_ENV[type] = env


def get_template(name, format="text", type="plugin"):
    if not _JINJA2_ENV:
        init()
    template_name = "{0}.{1}.jinja2".format(name, format)
    try:
        return _JINJA2_ENV[type].get_template(template_name)
    except jinja2.TemplateNotFound:
        print("Missing template {0}/{1}!".format(type, template_name), file=sys.stderr)
