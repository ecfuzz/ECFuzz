from typing import List, Tuple


def readCSVFile(filename: str) -> Tuple[List[str], List[List[str]]]:
    """
    The readCSVFile function reads a CSV file and returns two values:
        - The first value is the header of the CSV file, which is a list containing all column names.
        - The second value is data, which contains one list for each row in the CSV file. Each of these lists
        contains all the column values for that row.

    Args:
        filename:str: Specify the name of the file that will be read

    Returns:
        A tuple of two lists
    """
    with open(filename, "r") as f:
        lines = f.readlines()
        header = lines[0].strip().split(',')
        data = [line.strip().split(',') for line in lines[1:]]
        for i in range(len(data)):
            data[i] = [int(x) for x in data[i]]
        return header, data
