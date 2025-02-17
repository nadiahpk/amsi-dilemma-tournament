#!/usr/bin/env python3

import argparse
import math
import numpy
import matplotlib.pyplot as plt
from utils.load_strategies import load_strategies
from utils.game import game
from utils.repeat import proportion_rep
import utils.parameters as parameters

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--exclude-textbook", action = "store_true")
parser.add_argument("-l", "--log-plot", action = "store_true")
args = parser.parse_args()

strategies = list(load_strategies().values())
strategies.sort(key = lambda strategy: strategy.name) #Sort by name.

if args.exclude_textbook:
	strategies = [strategy for strategy in strategies if strategy.owner != "Textbook"]

proportions = [1 / len(strategies)] * len(strategies)
results = numpy.array(proportions)

#Runs all the games for a generation, returning a list of the proportions in the following generation.
def run_generation(proportions):
	payoffs = [0] * len(strategies)
	for i1, proportion1 in enumerate(proportions):
		for i2, proportion2 in enumerate(proportions):
			for _ in range(parameters.runs_per_pair):
				payoff1, payoff2 = game(strategies[i1], strategies[i2])
				payoffs[i1] += payoff1 * proportion1 * proportion2
				payoffs[i2] += payoff2 * proportion1 * proportion2
	
	proportions = [payoff / sum(payoffs) for payoff in payoffs]
	return proportions

#Run the evolution!
generations = range(parameters.num_gen+1)
for gen in generations[1:]:
	print(f"Generation {gen}")
	proportions = run_generation(proportions)
	results = numpy.vstack((results, numpy.array(proportions)))

#Save the results to a csv.
numpy.savetxt("results.csv",
	numpy.column_stack((numpy.array(generations), results)),
	fmt = ["%d"] + ["%.10f"] * len(strategies),
	delimiter = ",",
	header = ",".join(["\"generation\""] + [f"\"{strategy.name}\"" for strategy in strategies]),
	comments = "",
)

#Show a plot of the results.
for i in range(results.shape[1]):
	ys = results[:,i]
	if args.log_plot:
		ys = [math.log(y) for y in ys]
	plt.plot(generations, ys, label = strategies[i].name)

plt.xlabel("Generation")
plt.ylabel("Log proportion of population" if args.log_plot else "Proportion of population")
plt.xlim(min(generations), max(generations))
if not args.log_plot:
	plt.ylim(0, 1)
plt.legend()

plt.show()
