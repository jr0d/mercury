# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os

import requests


def chunk(l, n):
    """Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_index(l, key, value):
    """Find the index of an element by key value, for lists of dicts
    Return: index or -1
    """
    return next((index for index, d in enumerate(l) if d[key] == value), -1)


def get_element(l, key, value):
    """Return the first element where key==value
    """
    idx = get_index(l, key, value)
    if idx != -1:
        return l[idx]


def build_index(l, key):
    """Build an O(1) index of a list using key, only works if key is unique
    """
    return dict((d[key], dict(d, index=index)) for index, d in enumerate(l))


def build_index_l(l, key):
    """Build an index using key for a list of dicts where key is not unique
    """
    our_dict = dict()
    for d in l:
        if key not in d:
            continue
        idx = d[key]
        if idx in our_dict:
            our_dict[idx].append(d)
        else:
            our_dict[idx] = [d]
    return our_dict
