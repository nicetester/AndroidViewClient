'''
Copyright (C) 2012-2017  Diego Torres Milano
Created on Dec 1, 2012

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Diego Torres Milano
'''
import re

__version__ = '13.1.6'


class Dumpsys:
    FRAMESTATS = 'framestats'
    GFXINFO = 'gfxinfo'
    MEMINFO = 'meminfo'

    ACTIVITIES = 'activities'
    TOTAL = 'total'
    VIEW_ROOT_IMPL = 'viewRootImpl'
    VIEWS = 'views'

    def __init__(self, adbclient, subcommand, *args):
        self.nativeHeap = -1
        self.dalvikHeap = -1
        self.total = 0
        self.views = -1
        self.activities = -1
        self.appContexts = -1
        self.viewRootImpl = -1
        self.gfxProfileData = []
        self.framestats = []
        if args:
            args_str = ' '.join(args)
        else:
            args_str = ''
        cmd = 'dumpsys ' + subcommand + (' ' + args_str if args_str else '')
        self.parse(adbclient.shell(cmd), subcommand, *args)

    @staticmethod
    def listSubCommands(adbclient):
        return Dumpsys(adbclient, '-l')

    @staticmethod
    def meminfo(adbclient, args=None):
        return Dumpsys(adbclient, Dumpsys.MEMINFO, args)

    def get(self, name):
        return getattr(self, name)

    def parse(self, out, subcommand, *args):
        if subcommand == Dumpsys.MEMINFO:
            self.parseMeminfo(out)
        elif subcommand == Dumpsys.GFXINFO:
            if Dumpsys.FRAMESTATS in args:
                self.parseGfxinfoFramestats(out)
            else:
                self.parseGfxinfo(out)
        elif '-l':
            # list dumpsys subcommands
            return out
        else:
            pass

    def parseMeminfo(self, out):
        m = re.search('Native Heap[ \t]*(\d+)', out, re.MULTILINE)
        if m:
            self.nativeHeap = int(m.group(1))
        m = re.search('Dalvik Heap[ \t]*(\d+)', out, re.MULTILINE)
        if m:
            self.dalvikHeap = int(m.group(1))
        m = re.search('Views:[ \t]*(\d+)', out, re.MULTILINE)
        if m:
            self.views = int(m.group(1))
        m = re.search('Activities:[ \t]*(\d+)', out, re.MULTILINE)
        if m:
            self.activities = int(m.group(1))
        m = re.search('AppContexts:[ \t]*(\d+)', out, re.MULTILINE)
        if m:
            self.appContexts = int(m.group(1))
        m = re.search('ViewRootImpl:[ \t]*(\d+)', out, re.MULTILINE)
        if m:
            self.viewRootImpl = int(m.group(1))

        m = re.search('TOTAL[ \t]*(\d+)', out, re.MULTILINE)
        if m:
            self.total = int(m.group(1))
        else:
            raise RuntimeError('Cannot find TOTAL in "' + out + '"')

    def parseGfxinfo(self, out):
        pass

    def parseGfxinfoFramestats(self, out):
        pd = '---PROFILEDATA---'
        m = re.search(r'%s.*?%s' % (pd, pd), out, re.DOTALL)
        if m:
            pdc = 0
            for d in m.group(0).splitlines():
                pda = d.split(',')
                if pda[0] == pd:
                    continue
                if pda[0] == 'Flags':
                    if pda[1] != 'IntendedVsync' and pda[13] != 'FrameCompleted':
                        raise RuntimeError('Unsupported gfxinfo version')
                    continue
                if pda[0] == '0':
                    # Only keep lines with Flags=0
                    self.gfxProfileData.append(pda[:-1])
                    self.framestats.append(int(pda[13]) - int(pda[1]))
        else:
            raise RuntimeError('No profile data found')

    @staticmethod
    def gfxinfo(adbclient, *args):
        return Dumpsys(adbclient, Dumpsys.GFXINFO, *args)
