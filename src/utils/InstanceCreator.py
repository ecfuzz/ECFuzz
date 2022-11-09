import importlib
import sys
import typing


class InstanceCreator(object):
    @staticmethod
    def getInstance(pathToClass, *args, **kwargs) -> typing.Any:
        """
        The getInstance function is a helper function that imports the class from
        the pathToClass string and instantiates an instance of it with the given args
        and kwargs. It returns None if there is an error importing or instantiating.

        Args:
            pathToClass: Specify the path to the class that is going to be instantiated
            *args: Pass a non-keyworded, variable-length argument list
            **kwargs: Pass a variable number of keyword arguments to a function

        Returns:
            An instance of the class specified by pathtoclass
        """
        try:
            tokens = pathToClass.split('.')
            targetModule = importlib.import_module('.'.join(tokens[:-1]))
            targetClass = getattr(targetModule, tokens[-1])
            instance = targetClass(*args, **kwargs)
        except Exception as e:
            print(e, file=sys.stderr)
            instance = None

        return instance
