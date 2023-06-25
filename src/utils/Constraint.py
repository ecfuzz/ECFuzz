import csv
from utils.UnitConstant import DATA_DIR
from utils.Configuration import Configuration

class Constraint(object):
    """
    Constraint contains how to generate values for different types of configuration items.
    """
    def __init__(self) -> None:
        self.project: str = Configuration.fuzzerConf['project']
        self.constraintPath: str = Configuration.putConf['constraint_path']

    def getConstraintMap(self) -> dict:
        dependency = dict()
        
        # baseConf = ConfAnalyzer.confItemsBasic
        # constraint_type_set = set()
        with open(self.constraintPath, mode = "r", encoding = "utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                tmp1 = []
                #Configuration Parameter B
                tmp1.append(row[2])
                #Dependency Taxonomy
                tmp1.append(row[0])
                if row[1] in dependency.keys():
                    dependency[row[1]].append(tmp1)
                else:
                    dependency[row[1]] = []
                    dependency[row[1]].append(tmp1)
                    
                tmp2 = []
                #Configuration Parameter A
                tmp2.append(row[1])
                #Dependency Taxonomy
                tmp2.append(row[0])
                if row[2] in dependency.keys():
                    dependency[row[2]].append(tmp2)
                else:
                    dependency[row[2]] = []
                    dependency[row[2]].append(tmp2)
                
                # if row[0] not in constraint_type_set:
                #     constraint_type_set.add(row[0])

        return dependency