import pkgutil, json
from functools import partial

def loadUIConfig(jsonFile):
    return json.loads(pkgutil.get_data('GUI.CONFIG', jsonFile))

MInjectDataConfigFunc = partial(loadUIConfig, 'MInjectDataDialog.json')
MJobMonitorConfigFunc = partial(loadUIConfig, 'MJobMonitor.json')
