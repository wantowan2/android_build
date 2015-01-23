#!/usr/bin/env python
# Copyright (C) 2012 The CyanogenMod Project
# Copyright (C) 2012/2013 SlimRoms Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import urllib2
import json
import re
from xml.etree import ElementTree

product = sys.argv[1];

if len(sys.argv) > 2:
    depsonly = sys.argv[2]
else:
    depsonly = None

try:
    device = product[product.index("_") + 1:]
except:
    device = product

if not depsonly:
    print "Device %s not found. Attempting to retrieve device repository from DU Github (http://github.com/DirtyUnicorns)." % device

repositories = []

page = 1
while not depsonly:
    result = json.loads
    if len(result) == 0:
        break
    for res in result:
        repositories.append(res)
    page = page + 1

local_manifests = r'.repo/local_manifests'
if not os.path.exists(local_manifests): os.makedirs(local_manifests)

# in-place prettyprint formatter
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def get_from_manifest(devicename):
    try:
        lm = ElementTree.parse(".repo/local_manifests/du_manifest.xml")
        lm = lm.getroot()
    except:
        lm = ElementTree.Element("manifest")

    for localpath in lm.findall("project"):
        if re.search("android_device_.*_%s$" % device, localpath.get("name")):
            return localpath.get("path")

    # Devices originally from AOSP are in the main manifest...
    try:
        mm = ElementTree.parse(".repo/manifest.xml")
        mm = mm.getroot()
    except:
        mm = ElementTree.Element("manifest")

    for localpath in mm.findall("project"):
        if re.search("android_device_.*_%s$" % device, localpath.get("name")):
            return localpath.get("path")

    return None

def is_in_manifest(projectname, branch):
    try:
        lm = ElementTree.parse(".repo/local_manifests/du_manifest.xml")
        lm = lm.getroot()
    except:
        lm = ElementTree.Element("manifest")

    for localpath in lm.findall("project"):
        if localpath.get("name") == projectname and localpath.get("revision") == branch:
            return 1

    return None

def add_to_manifest(repositories):
    try:
        lm = ElementTree.parse(".repo/local_manifests/du_manifest.xml")
        lm = lm.getroot()
    except:
        lm = ElementTree.Element("manifest")

    for repository in repositories:
        repo_name = repository['repository']
        repo_target = repository['target_path']
        existing_project = exists_in_tree_device(lm, repo_name)
        if existing_project != None:
            if existing_project.attrib['revision'] == repository['branch']:
                print 'DirtyUnicorns/%s already exists' % (repo_name)
            else:
                print 'updating branch for DirtyUnicorns/%s to %s' % (repo_name, repository['branch'])
                existing_project.set('revision', repository['branch'])
            continue

        print 'Adding dependency: DirtyUnicorns/%s -> %s' % (repo_name, repo_target)
        project = ElementTree.Element("project", attrib = { "path": repo_target,
            "remote": "github", "name": "DirtyUnicorns/%s" % repo_name, "revision": "lollipop" })

        if 'branch' in repository:
            project.set('revision', repository['branch'])

        lm.append(project)

    indent(lm, 0)
    raw_xml = ElementTree.tostring(lm)
    raw_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + raw_xml

    f = open('.repo/local_manifests/du_manifest.xml', 'w')
    f.write(raw_xml)
    f.close()

