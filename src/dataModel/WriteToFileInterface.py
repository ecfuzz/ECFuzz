from abc import ABCMeta, abstractmethod
import os


class WriteToFileInterface(object, metaclass=ABCMeta):
    """
    This interface requires for realizing a function that write itself to file.
    """

    def __init__(self) -> None:
        self.fileDir: str = '.'
        self.fileName: str = ''
        self.filePath: str = ''
    
    def writeToFile(self, fileName: str = None) -> str:
        """
        write self to file.

        Returns:
            str: a new file name
        """
        if not os.path.exists(self.fileDir):
            os.mkdir(self.fileDir)

        if self.fileName.__len__() == 0 :
            if fileName:
                filePath = os.path.join(self.fileDir, fileName)
            else:
                filePath = os.path.join(self.fileDir, self.generateFileName())
        else:
            filePath = os.path.join(self.fileDir, self.fileName)

        self.filePath = filePath

        with open(filePath, 'w') as f:
            f.write(str(self))

        return filePath

    @abstractmethod
    def generateFileName(self) -> str:
        """generate a new file name which would be used create a file to store self.

        Returns:
            str: a new file name
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass