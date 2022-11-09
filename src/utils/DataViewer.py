import os.path
import threading
import time

import numpy as np
import visdom

from utils import CSVReader
from utils.Configuration import Configuration
from utils.ShowStats import ShowStats


class DataViewer(object):
    def __init__(self, env='fast configuration fuzzing'):
        self.fuzzerConf = Configuration.fuzzerConf
        self.vis = visdom.Visdom(server=self.fuzzerConf['data_viewer_server_address'],
                                 port=int(self.fuzzerConf['data_viewer_server_port']),
                                 env=env)
        self.stop = False

    def run(self):
        self.drawText()
        self.drawData(None)
        cnt: int = 0
        while True:
            if self.stop:
                break
            time.sleep(1)
            cnt += 1
            self.drawText()
            if cnt % 10 == 0:
                self.drawData()

    def drawText(self) -> None:
        """
        The drawText function draws the text on the visdom web interface.
        It draws project name, time used, last new failed unit test, last new failed system test and so on.
        """
        projectName = self.fuzzerConf['project']

        timeUsed = int(ShowStats.runTime)
        timeUnit = 'seconds'
        if timeUsed > 864000:
            timeUsed //= 86400
            timeUnit = 'days'
        elif timeUsed > 18000:
            timeUsed //= 3600
            timeUnit = 'hours'
        elif timeUsed > 60:
            timeUsed //= 60
            timeUnit = 'minutes'

        text = f"""
<font color="GoldenRod" ><b>Fast Configuration Fuzzing</font> 
(<font color="GreenYellow ">{projectName}</font>)</b><br/>
------------------------------<font color="DodgerBlue "><b>Time</b></font>-----------------------------------------<br/>
<b>&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;run time</b>: {ShowStats.getTime(round(ShowStats.runTime))}<br/>
<b>&emsp;&ensp;last new failed unit test</b>: {ShowStats.getTime(round(ShowStats.lastNewFailUnitTest))}<br/>
<b>last new failed system test</b>: {ShowStats.getTime(round(ShowStats.lastNewFailSystemTest))}<br/>
<b>&emsp;&ensp;&emsp;longest unit test time</b>: {ShowStats.getTime(round(ShowStats.longgestUnitTestTime))}<br/>
<b>&emsp;longest system test time</b>: {ShowStats.getTime(round(ShowStats.longgestSystemTestTime))}<br/>
<b>&emsp;&emsp;&ensp;average unit test time</b>: {ShowStats.getTime(round(ShowStats.averageUnitTestTime))}<br/>
<b>&emsp;average system test time</b>: {ShowStats.getTime(round(ShowStats.averageSystemTestTime))}<br/>
------------------------------<font color="DodgerBlue "><b>Mutation</b></font>------------------------------------<br/>
<b>&emsp;&emsp;&emsp;&emsp;&emsp;mutation strategy</b>: {ShowStats.mutationStrategy}<br/>
<b>&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;now mutate type</b>: {ShowStats.nowMutationType}<br/>
<b>now test configuration item</b>: {ShowStats.nowTestConfigurationName}<br/>
<b>&emsp;&emsp;&emsp;&emsp;&ensp;total unit test cases</b>: {ShowStats.totalUnitTestcases}<br/>
<b>&emsp;&emsp;total run unit test count</b>: {ShowStats.totalRunUnitTestsCount}<br/>
<b>&emsp;&emsp;&emsp;total system test cases</b>: {ShowStats.totalSystemTestcases}<br/>
<b>&emsp;&emsp;&emsp;&emsp;unit test exec spped</b>: {ShowStats.unitTestExecSpeed}/sec<br/>
<b>&emsp;&emsp;&ensp;system test exec speed</b>: {ShowStats.systemTestExecSpeed}<br/>
------------------------------<font color="DodgerBlue "><b>Overall Results</b></font>------------------------------<br/>
<b>&emsp;&emsp;&emsp;&emsp;fuzzing progress</b>: {ShowStats.loopCounts}:{ShowStats.iterationCounts}({ShowStats.currentJob})<br/>
<b>&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;queue length</b>: {ShowStats.queueLength}<br/>
<b>&emsp;&ensp;total unit test failures</b>: {ShowStats.totalUnitTestFailed}<br/>
<b>total system test failures</b>: <font color="red">{ShowStats.totalSystemTestFailed}</font><br/>
"""
        self.vis.text(text, win='text')

    def drawData(self, update='update') -> None:
        if not os.path.exists(self.fuzzerConf['plot_data_path']):
            return
        header, data = CSVReader.readCSVFile(self.fuzzerConf['plot_data_path'])
        data = np.array(data, dtype=np.int64)
        timestack = data[:, 0]
        data = data[:, 1:]
        self.vis.line(data, timestack, win='data', update=update,
                      opts=dict(legend=header[1:],
                                showlegend=True,
                                markers=False,
                                title='DataView',
                                xlabel='Time',
                                ylabel='',
                                fillarea=False))


def startDrawing(dataViewer: DataViewer):
    threading.Thread(target=dataViewer.run).start()


def stopDrawing(dataViewer: DataViewer):
    dataViewer.stop = True
