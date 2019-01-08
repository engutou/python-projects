#! python

import csv

if __name__ == "__main__":
    csv_reader = csv.reader(open("data/test.csv"))
    for row in csv_reader:
        print(row)
