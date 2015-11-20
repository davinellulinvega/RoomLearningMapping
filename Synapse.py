#!/usr/bin/python
__author__ = 'davinellulinvega'

# Import the required packages
from random import uniform
import Neuron


#Define the Synapse class
class Synapse:
	"""The basic connection between computing units in the neural network"""

	def __init__(self, neuron_in, neuron_out):
		"""Define the synapse's attribute and initialize their value"""

		#Initialize the weight to a random number between 0 and 1
		self.weight = uniform(-1, 1)
		#Keep a record of the previous delta, to compute the momentum
		self.prev_delta = 0
		self.eta = 0.01  # 0.0001
		self.epsylon = 0.7
		#Check if neuron_in is an instance of Neuron
		if not(isinstance(neuron_in, Neuron.Neuron)):
			#If not raise an error
			raise TypeError("Only neurons can be connected to a synapse")
		else:
			#Else store the instance
			self.neuron_in = neuron_in
		#Check if neuron_out is an instance of Neuron
		if not(isinstance(neuron_out, Neuron.Neuron)):
			#If not raise an error
			raise TypeError("Only neurons can be connected to a synapse")
		else:
			#Else store the instance
			self.neuron_out = neuron_out

	def update_weight(self):
		"""Define the procedure for updating the weight of the synapse"""

		#Compute the delta
		delta = self.eta * self.neuron_out.error * self.neuron_in.output + self.epsylon * self.prev_delta
		#Compute the new weight
		self.weight += delta
		#Store the delta in the previous delta
		self.prev_delta = delta

	def get_weighted_input(self):
		"""Returns the value of the neuron_in multiplied by the weight of the synapse"""

		return self.weight * self.neuron_in.output
