#!/usr/bin/python
__author__ = 'davinellulinvega'

#Import the required packages
import Layer


#Define the Network class
class Network:
	"""Define a simple feed forward network, with an input, a hidden layer and an output layer"""

	def __init__(self, nb_in, hid_layers, nb_out):
		"""Define the attributes and assign default values"""

		#Define an input layer
		self.input = Layer.Layer(nb_in)
		#Define the hidden layers
		self.hidden = []

		#Check that hid_layers is a list
		if not(isinstance(hid_layers, list)):
			#Raise a Type error
			raise TypeError("You should provide a list of number of neurons for the hidden layers")
		#Build the hidden layers
		for index, nb_neuron in enumerate(hid_layers):
			#Check if it is the first index
			if index == 0:
				#Create a layer linked to the input
				self.hidden.append(Layer.Layer(nb_neuron, self.input))
			else:
				#Create a layer linked to the previous one
				self.hidden.append(Layer.Layer(nb_neuron, self.hidden[index - 1]))

		#Define an output layer
		self.output = Layer.Layer(nb_out, self.hidden[-1])

	def update_weight(self):
		"""Define the procedure to update the synaptic weights"""

		#Update the output layer
		self.output.update_weight()
		#Update the hidden layers in reverse order
		for hidden in reversed(self.hidden):
			hidden.update_weight()

	def update_error(self, error):
		"""Define the procedure to update the neurons' errors"""

		#Check that the error is a list of the same size than the output layer
		if not(isinstance(error, list)) or len(error) != len(self.output.neurons):
			#Raise and error
			raise IndexError("Error is not a list or has not the right amount of entries", len(error), len(self.output.neurons))
		#Update the output layer
		self.output.update_error(error)
		#Update the hidden layers in reverse order
		for hidden in reversed(self.hidden):
			hidden.update_error()

	def learn(self, error):
		"""Define the procedure to the network to learn"""

		#Update the error
		self.update_error(error)
		#Update the weights
		self.update_weight()

	def activate(self, input_val):
		"""Define the procedure to compute the new output of each neurons"""

		#Check if the provided input is a list of the same size as the input layer
		if not(isinstance(input_val, list)):
			raise TypeError("Input values should be provided in a list")
		if len(input_val) != len(self.input.neurons):
			raise IndexError("The number of input values provided is different from the number of input neurons",
			                 len(input_val), len(self.input.neurons))

		#Assign the values to the neurons in the input layer
		for index, value in enumerate(input_val):
			self.input.neurons[index].output = value

		#Activate the hidden layers in reverse order
		for hidden in reversed(self.hidden):
			hidden.activate()
		#Activate the output layer
		self.output.activate()

	def get_output(self):
		"""Retrieve the value(s) of the output(s) and return them in a list"""

		#Initialize the list
		outputs = []
		#For each neuron in the list
		for tmp_neuron in self.output.neurons:
			#Append the output to the list
			outputs.append(tmp_neuron.output)
		#Return the resulting list
		return outputs
