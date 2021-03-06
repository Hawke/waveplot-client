#!/usr/bin/env python 
# Copyright 2013 Ben Ockmore

 # This file is part of WavePlot.

 # WavePlot is free software: you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by
 # the Free Software Foundation, either version 3 of the License, or
 # (at your option) any later version.

 # WavePlot is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.

 # You should have received a copy of the GNU General Public License
 # along with WavePlot. If not, see <http://www.gnu.org/licenses/>.

import subprocess
import base64
import urllib
import urllib2
import mutagen.flac
import mutagen.id3
import mutagen.oggvorbis
import os
import sys
import tempfile

VERSION = "BANNANA"
EDITOR_KEY = ""

exe_file = "WavePlotImager"
if sys.platform == "win32":
    exe_file += ".exe"

def FindExe():
    global exe_file
    for directory, directories, filenames in os.walk("."):
        for filename in filenames:
            if filename==exe_file:
                exe_file = os.path.abspath(os.path.join(directory,filename))
                return

dumpdir = os.path.abspath(".")

FindExe()

print "Using executable: " + exe_file

if EDITOR_KEY == "":
    EDITOR_KEY = input("\nPlease enter your activation key below:\n")
    print "To avoid doing this in future, open up your scanner.py file and find the line starting EDITOR_KEY. Put your key between the quote marks!\n"


for directory, directories, filenames in os.walk("."):
    for filename in filenames:
        recording_id = ""
        release_id = ""
        track_num = ""
        disc_num = ""
        file_ext = os.path.splitext(filename)[1][1:]
        in_path = os.path.realpath(os.path.join(directory,filename))
        audio = mutagen.File(os.path.join(directory,filename),easy=True)
        if audio:
            if "musicbrainz_trackid" in audio:
                recording_id = audio["musicbrainz_trackid"][0]
            if "musicbrainz_albumid" in audio:
                release_id = audio["musicbrainz_albumid"][0]
            if "tracknumber" in audio:
                track_num = audio["tracknumber"][0].split('/')[0].strip()
            if "discnumber" in audio:
                disc_num = audio["discnumber"][0].split('/')[0].strip()

        if (recording_id != "") and (release_id != "") and (track_num != "") and (disc_num != ""):
            output = subprocess.check_output([exe_file,in_path,VERSION])

            output = output.partition("WAVEPLOT_START")[2]

            image_data, sep, output = output.partition("WAVEPLOT_LARGE_THUMB")
            if sep == "":
                raise ValueError

            large_thumbnail, sep, output = output.partition("WAVEPLOT_SMALL")
            if sep == "":
                raise ValueError

            small_thumbnail, sep, output = output.partition("WAVEPLOT_INFO")
            if sep == "":
                raise ValueError

            info, sep, output = output.partition("WAVEPLOT_END")
            if sep == "":
                raise ValueError

            image_data = base64.b64encode(image_data)

            large_thumbnail = base64.b64encode(large_thumbnail)

            small_thumbnail = base64.b64encode(small_thumbnail)

            length, trimmed, sourcetype, num_channels = info.split("|")

            url = 'http://pi.ockmore.net:19048/submit'

            values = {'recording' : recording_id,
                      'release' : release_id,
                      'track' : track_num,
                      'disc' : disc_num,
                      'image' : image_data,
                      'large_thumb' : large_thumbnail,
                      'small thumb' : small_thumbnail,
                      'editor' : EDITOR_KEY,
                      'length' : length,
                      'trimmed' : trimmed,
                      'source' : sourcetype,
                      'num_channels': num_channels,
                      'version' : VERSION }

            data = urllib.urlencode(values)
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req)
            the_page = response.read()

            print the_page
