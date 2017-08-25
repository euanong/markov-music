import random
import midi
import datetime

class Markov(object):
	"""docstring for Markov"""
	def __init__(self, order=2):
		super(Markov, self).__init__()
		self.order = order
		self.chain = {}

	def add(self,key,value):
		if self.chain.has_key(key):
			self.chain[key].append(value)
		else:
			self.chain[key] = [value]

	def load(self,midifile):
		pattern = midi.read_midifile(midifile)
		#track = pattern[1]
		for track in pattern:
			noteslist = []
			curoffset = 0
			for i in track:
				if i.name == "Note On" and i.data[1]!=0:
					note = (i.data[0],i.data[1],i.tick+curoffset)
					#note = (i.data[0],i.data[1],i.tick)
					noteslist.append(note)
					curoffset = 0
				else:
					curoffset+=i.tick
			if len(noteslist)>self.order:
				for j in range(self.order,len(noteslist)):
					t = tuple(noteslist[j-self.order:j])
					print t
					print noteslist[j]
					self.add(t,noteslist[j])
			else:
				print "Corpus too short"
		
	def generate(self,length,filename):
		pattern = midi.Pattern()
		# Instantiate a MIDI Track (contains a list of MIDI events)
		track = midi.Track()
		# Append the track to the pattern
		pattern.append(track)

		tick = 0
		currenttuple = random.choice(self.chain.keys())
		prevnote = False
		for i in range(0,self.order):
			if prevnote!=False:
				on = midi.NoteOnEvent(tick=tick, velocity=0, pitch=prevnote)
				track.append(on)
			on = midi.NoteOnEvent(tick=0, velocity=currenttuple[i][1], pitch=currenttuple[i][0])
			track.append(on)
			tick = currenttuple[i][2]
			prevnote = currenttuple[i][0]
		result = random.choice(self.chain[currenttuple])
		#print currenttuple
		for i in range(1,length):
			for j in range(0,self.order):
				if prevnote!=False:
					if tick>5000:
						tick=5000
					on = midi.NoteOnEvent(tick=tick, velocity=0, pitch=prevnote)
					track.append(on)
				on = midi.NoteOnEvent(tick=0, velocity=currenttuple[j][1], pitch=currenttuple[j][0])
				track.append(on)
				tick = currenttuple[j][2]
				prevnote = currenttuple[j][0]

			currenttuple = list(currenttuple)
			currenttuple.pop(0)
			currenttuple.append(result)
			currenttuple = tuple(currenttuple)
			if self.chain.has_key(currenttuple):
				result = random.choice(self.chain[currenttuple])
			else:
				result = random.choice(self.chain[random.choice(self.chain.keys())])
		# Add the end of track event, append it to the track
		eot = midi.EndOfTrackEvent(tick=1)
		track.append(eot)
		# Print out the pattern
		print pattern
		# Save the pattern to disk
		midi.write_midifile(filename+".mid", pattern)

if __name__ == '__main__':
	directory = "compositions"
	musicdir = "input"

	musicdir+="/"
	logname = directory+"/"+"{:%Y-%m-%d-%H:%M:%S}_genmusic".format(datetime.datetime.now())

	m = Markov(3)
	print "Loading music"
	inp = raw_input('Name of midi file to load or g to generate: ')
	while inp!="g":
		try:
			m.load(musicdir+inp)
		except Exception as e:
			print "File not found or corrupt"
		inp = raw_input('Name of midi file to load or g to generate: ')
	print "Done"
	print m.chain
	m.generate(1000,logname)