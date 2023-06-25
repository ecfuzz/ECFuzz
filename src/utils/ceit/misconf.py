from logging import Logger
import logging
from utils.Configuration import Configuration
from utils.ceit.misconf_generator.ConfErr.confErr import ConfErr
from utils.ceit.misconf_generator.ConfTest.confTest import ConfTest
from utils.ceit.misconf_generator.Fuzzing.Fuzzing import Fuzzing
from utils.ceit.misconf_generator.ConfDiagDetector.confDiagDetector import ConfDiagDetector
from utils.ceit.misconf_generator.CaseAlt.caseAlt import CaseAlt
from utils.Logger import getLogger

errs = {"name": None,
        "key": None,
        "operator": None,
        "value": None}

class MisconfEngine( object ):

    def __init__(self):
        self.logger = getLogger()
        self.misconf_mode = Configuration.fuzzerConf['misconf_mode']

    def mutate(self, option):
        self.logger.info(f">>>>[MisconfEngine] misconf_mode : {self.misconf_mode}")
        if self.misconf_mode == "Fuzzing":
            fuzzing = Fuzzing( option )
            errs = fuzzing.get_misconfs()
            return errs
        elif self.misconf_mode == "ConfErr":
            conferr = ConfErr( option )
            errs = conferr.get_misconfs()
            return errs
        elif self.misconf_mode == "ConfTest":
            conftest = ConfTest( option )
            errs = conftest.get_misconfs()
            return errs
        elif self.misconf_mode == "ConfDiagDetector":
            confdiagdetector = ConfDiagDetector( option )
            errs = confdiagdetector.get_misconfs()
            return errs
        elif self.misconf_mode == "CaseAlt":
            casealt = CaseAlt( option )
            errs = casealt.get_misconfs()
            return errs
        else:
            self.logger.info( "misconf_mode could not recognize." )
