import random
import os
import argparse

prefix = "java Toss"
w = ['Cloudy', 'Clear']
t = ['Day', 'Night']
parser = argparse.ArgumentParser()
parser.add_argument("runs", help="Number of tests to run", type=int)
args = parser.parse_args()

for i in range(args.runs):
    command = "{} {} {}".format(prefix, random.choice(w), random.choice(t))
    print("Running: " + command)
    os.system(command)


