#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################

GUI_PLUGIN_PATH = __path__[0]
import unipath

class MPluginManager(object):
    @classmethod
    def loadPlugins(self, sender, event):
        resultList = []
        pluginFolder = unipath.Path(GUI_PLUGIN_PATH).child(event)
        if pluginFolder.exists():
            for i in pluginFolder.listdir(pattern='M*.py', filter=unipath.FILES):
                try:
                    pluginName = str(i.stem)
                    plugin = __import__('GUI.PLUGINS.%s.%s' % (event, pluginName), fromlist=[pluginName])
                    classObj = getattr(plugin, pluginName)
                    resultList.append(classObj())
                except:
                    import traceback
                    print traceback.print_exc()
        return resultList
