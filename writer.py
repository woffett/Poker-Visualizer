import csv
import sys
from parsing import process

FIELDNAMES = ['player','ID','depth','actions','members','parent','children']

def writer(inputFile, outputFile):
    '''
    arguments:
        - inputFile is the path to a game file
        - outputFile is the name of the CSV to be written
    writes the contents of inputFile to a CSV specified by outputFile
    '''

    p1, p2 = process(inputFile)

    with open(outputFile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES,
                                delimiter='\t',quotechar='\"')

        writer.writeheader()

        for infoset in p1.values():
            writer.writerow(infoset.toDict())

        for infoset in p2.values():
            writer.writerow(infoset.toDict())


if __name__ == '__main__':
    if len(sys.argv) > 2:
        gamefile = sys.argv[1]
        outputFile = sys.argv[2]
        writer(gamefile, outputFile)
    else:
        print('Usage: python writer.py <path/to/gamefile> <path/to/outputCSV>')
        
