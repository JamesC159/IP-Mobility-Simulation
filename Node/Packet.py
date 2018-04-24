class Packet:
	def __init__(self, srcIP = None, dstIP = None, pld = None):
		self.src = srcIP
		self.dst = dstIP
		self.payload = pld

	def toString(self):
		if self.src and self.dst and self.payload:
			return self.src + " " + self.dst + " " + self.payload
		elif self.payload:
			return self.payload
		else:
			return "Empty packet"