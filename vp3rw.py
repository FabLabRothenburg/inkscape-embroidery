#!python
#!/usr/bin/python
# (c) Kalle Pungas 2014
# licence: GPLv3

import sys
import struct
import random

#def abs(x):
#	if (x<0): return -x
#	return x

def sgn(x):
	if x>0: return 1
	if x<0: return -1
	return 0

def clamp(v):
	if v> 30: v =  30 # 127
	if v<-30: v = -30
	return v

def rnd_slen():
	s=int(random.uniform(20,40)) # random stitch length 2..4 mm
	# todo: get stitch length range from user interface
	return s


def div2(x,y):
	if y==0: return None
	return x/y

def clamp2(x,y,long):
	''' todo: join too short stitches
	global prev_k
	k=div2(x,y) # atan2
	if abs(x)+abs(y) < min_stitch_len and k==prev_k: 
	prev_k=k
	'''
	if long: 
		slen=127
	else:
		slen=rnd_slen()
	sgnx=sgn(x)
	sgny=sgn(y)
	xx=abs(x)
	yy=abs(y)
	if xx>yy:
		if xx>slen: return slen*sgnx,int(slen*yy/xx)*sgny # linear interpolate
	else:
		if yy>slen: # 127
			return int(slen*xx/yy)*sgnx,slen*sgny # linear interpolate
	return x,y


def decode_color(htmlcolor):  #   #rrggbb
	# todo: trim(), check for '#', accept different size: #rgb #rrggbb #rrrgggbbb. accept color name
	# todo: check if first char is really #
#	if len(htmlcolor)==0: return 0,0,0
	r=int(htmlcolor[1:3],16)
	g=int(htmlcolor[3:5],16)
	b=int(htmlcolor[5:7],16)
	#print "r=",r,"g=",g,"b=",b
	return r,g,b



# 8 bit string -> str length char + 16 bit big endian string
	
def n_wstr(s):
	s1,s2=divmod(len(s)*2,256)
	ss=chr(s1)+chr(s2)
	for c in s: ss += chr(0) + c # 16-bit big-endian
	return ss

def n_str(s):
	s1,s2=divmod(len(s),256)
	ss=chr(s1)+chr(s2)
	ss += s # 16bit pikkus + 8bit string
	return ss


def int2str(i_int,b_ytes):  # 2, 4
	s=""
	for r in reversed(range(b_ytes)): # bytes=2  > shift=8,0  bytes=4  > shift=24,16,8,0
		shift=r*8
		s+=chr((i_int >> shift) & 255)
	return s


def vp3_colour_table(r=50,g=50,b=50):
	table=chr(0)+chr(r)+chr(g)+chr(b)+chr(0)+chr(0)
	return table



def read_verify_str(f,s):
	s2=f.read(len(s))
	print hexdump(s2),"# %s",s2
	if s2!=s: 
		print " # ERR: must be %s ***********************************" % s # s
		errors+=1

def read_verify_int(f,size_bytes,value,comment=""):
	value2=readint(f,size_bytes)
	if size_bytes==1:
		print "%02x # %s" % (value2,comment)
	else:
		print "%x # %s" % (value2,comment)
	if value2!=value: print " # ERR: must be %x *******************************" % value # s

def read_explain_int(f,size_bytes,comment,signed=1):
	s=f.read(size_bytes)
	h=hexdump(s)
	if signed:
		value2=str2intsgn(s)
	else:
		value2=str2int(s)
	print "%s #int%d %d %s" % (h,size_bytes, value2, comment)
	return value2


def readint4(f):
	return struct.unpack("i",f.read(4))[0]


def str2int(s): # binary as str to unsigned int
	t=0
	for i,c in enumerate(reversed(s)): t+=ord(c) << i*8 
	return t


def str2intsgn(s): # binary as str to signed integer
	t=0
	if s=="": return 0 # error in vp3 file
	if ord(s[0])>=80:
		for i,c in enumerate(reversed(s)): t+=((~ord(c))& 255) << i*8 # invert c as byte
		return -t-1
	else:
		for i,c in enumerate(reversed(s)): t+=ord(c) << i*8 
		return t
    

def readint(f,size_bytes):
	s=f.read(size_bytes)
	t=0
	for i,c in enumerate(reversed(s)): t+=ord(c) << i*8
	return t

def read_n_wstr(f,comment):
	strl=readint(f,2)
	print hexdump(int2str(strl,2))," #=%d strlen of %s " % (strl,comment)
	s=f.read(strl)
	print hexdump(s) 
	print "# ",s


def hexdump(s):
	h=""
	for c in s: h+="%02x " % ord(c)
	return h

def read_verify_bytestr(f,bytes_hex_str,comment):
	s=f.read(len(bytes_hex_str)/2)
	s_hex=""
	s_hex_vis=""
	for c in s: 
		s_hex+="%02x" % ord(c)
		s_hex_vis+="%02x " % ord(c)
	print s_hex_vis," # ",comment
	if s_hex!=bytes_hex_str: print " # *****ERR: must be ",bytes_hex_str

def explain(fname): # decode vp3 file, better alternative to viewing file with hexdump
	f=open(fname,"rb")
	read_verify_str(f,"%vsm%")
	read_verify_int(f,1,0)
	read_n_wstr(f,"producer")
	read_verify_bytestr(f,"000200","embroidery tag 020")
	read_explain_int(f,4,"embroidery size")
	read_n_wstr(f,"human readable notes")
	read_explain_int(f,4,"extent right")
	read_explain_int(f,4,"extent top")
	read_explain_int(f,4,"extent left")
	read_explain_int(f,4,"extent bottom")
	read_explain_int(f,4,"stitch time count")
	read_explain_int(f,2,"thread change count",0)
	read_verify_bytestr(f,"0c","unknown 12")
	read_explain_int(f,2,"unknown 00 01")
	read_verify_bytestr(f,"000300","hoop tag 030")
	read_explain_int(f,4,"hoop len")
	read_explain_int(f,4,"centre X of summary extent")
	read_explain_int(f,4,"centre Y of summary extent")
	read_verify_bytestr(f,"000000","unknown 00 00 00")
	read_explain_int(f,4,"hoop left")
	read_explain_int(f,4,"hoop right")
	read_explain_int(f,4,"hoop bottom")
	read_explain_int(f,4,"hoop top")
	read_explain_int(f,4,"hoop width",0)
	read_explain_int(f,4,"hoop height",0)
	read_n_wstr(f,"second copy of settings string")
	read_verify_bytestr(f,"6464","unknown 64 64")
	read_verify_bytestr(f,"00001000","unknown 4096")
	read_verify_bytestr(f,"00000000","unknown 0")
	read_verify_bytestr(f,"00000000","unknown 0")
	read_verify_bytestr(f,"00001000","unknown 4096")
	read_verify_str(f,"xxPP")
	read_verify_bytestr(f,"0100","unknown 01 00")
	read_n_wstr(f,"second copy of producer string")
	thread_count=read_explain_int(f,2,"thread count",0)
	didread050=0
	for thread in xrange(thread_count):
		if didread050==0: read_verify_bytestr(f,"000500","thread tag 050 ------------------------------------------")
		else: print "# ERR: adjusted thread tag 050 position -----------------------------------------------"
		didread050=0
		thread_len=read_explain_int(f,4,"thread len")
		startx=read_explain_int(f,4,"startx")
		starty=read_explain_int(f,4,"starty")
		colors_per_thread=read_explain_int(f,1,"colors per thread",0)
		for color in xrange(colors_per_thread):
			read_explain_int(f,1,"color table const 0")
			read_explain_int(f,1,"color table R",0)
			read_explain_int(f,1,"color table G",0)
			read_explain_int(f,1,"color table B",0)
			read_explain_int(f,1,"color table const 0")
			read_explain_int(f,1,"color table const 0")
		read_explain_int(f,1,"unknown 0")
		read_explain_int(f,1,"thread type tenstion 5=rayon 1=metallic")
		read_explain_int(f,1,"thread weight km/kg")
		read_n_wstr(f,"code")
		read_n_wstr(f,"maker")
		read_n_wstr(f,"manu,material,weight")
		read_explain_int(f,4,"total displacement X")
		read_explain_int(f,4,"total displacement Y")
		read_verify_bytestr(f,"000100","stitch tag 010")
		stitches_len=read_explain_int(f,4,"stitches len")
		read_explain_int(f,1,"scale x")
		read_explain_int(f,1,"scale y")
		read_explain_int(f,1,"unk 0")
		l=stitches_len-3 # +1
		x=99
		y=99
		while l>0:
			prex=x
			prey=y
			x=readint(f,1)
			if (l<20) and (prex==0) and (prey==5) and (x==0):
				print "# WARN: thread tag encountered in stitches: l was %d" % l
				didread050=1
				l=0 # break;
			y=readint(f,1)
			p="%02x %02x" % (x,y)
			if (l<20) and (prey==0) and (x==5) and (y==0):
				print "# WARN: thread tag encountered in stitches: l was %d" % l
				didread050=1
				l=0 # break;
			l-=2
			if x==128:
				if y==1:
					xx=readint(f,2)
					yy=readint(f,2)
					p+=" "+hexdump(int2str(xx,2))+hexdump(int2str(yy,2))
					# p+=" %03d %03d" % (xx,yy)
					x=readint(f,1)
					y=readint(f,1)
					p+= " %02x %02x" % (x,y)
					l-=6
				if y==3: p+=" # 80+03"
			print p
		if didread050==0: read_verify_int(f,1,0,"0, end of stitches")
	f.close()


class vp3:
	lines=""
	cnt=0
	stitches=[]
	#headers=[]
	colors=[]
	startx=[]
	starty=[]
	endx=[]
	endy=[]
	header=""
	posx=None
	posy=None
	max_x=-100000
	max_y=-100000
	min_x=100000
	min_y=100000
	total_displacement_x=0
	total_displacement_y=0
	stitch_time_count=0
	embroidery_len=0
	centre_x=0
	centre_y=0
	min_stitch_len=1 # 5 for eliminating small stitches
	#prev_startx=None
	#prev_starty=None
	
	def __init__(self,producer="vp3rw",settings="settings"):
		self.producer=producer
		self.settings=settings
		self.posx=None
		self.posy=None


	def mkstitch(self,colorindex): # create color header thread-details
		colorhtml=self.colors[colorindex]
		r,g,b=decode_color(colorhtml)
		s=chr(0)+chr(5)+chr(0) # tag: thread packet
		#s1=int2str(0,4) # try startx 0
		#s1+=int2str(0,4)
		

		start_x=self.startx[colorindex]-(self.max_x+self.min_x)*50 # * 100 / 2
		start_y=self.starty[colorindex]-(self.max_y+self.min_y)*50
		'''
		if colorindex==0:
			start_x=self.startx[colorindex]-(self.max_x+self.min_x)*50 # * 100 / 2
			start_y=self.starty[colorindex]-(self.max_y+self.min_y)*50
		else:
		# startdiks v6etakse eelmise end, va esimesel kus v6etakse oma start
			start_x=self.endx[colorindex-1]-(self.max_x+self.min_x)*50 # * 100 / 2
			start_y=self.endy[colorindex-1]-(self.max_y+self.min_y)*50
		'''
		end_x=self.endx[colorindex]-(self.max_x+self.min_x)*50 # * 100 / 2
		end_y=self.endy[colorindex]-(self.max_y+self.min_y)*50
		
		dispx=end_x-start_x # -self.prev_startx
		dispy=end_y-start_y #-self.prev_starty
		s1=int2str(start_x,4)
		s1+=int2str(start_y,4)
		s1+=chr(1) # colors per thread
		s1+=vp3_colour_table(r,g,b)
		s1+=chr(0)+chr(5)+chr(0x28)
		thread_description=n_str("%04d" % colorindex)+n_str("thread humanreadable name")+n_str("thread maker material weight")
		s1+=thread_description
		

		#s1+=int2str(0,4)
		#s1+=int2str(0,4)
		s1+=int2str(dispx,4) # displacement
		s1+=int2str(dispy,4)
		#self.prev_startx=start_x
		#self.prev_starty=start_y
		
		s1+=chr(0)+chr(1)+chr(0)
		stitches_len=len(self.stitches[colorindex])
		s1+=int2str(stitches_len+3,4)
		s1+=chr(10) # scale-x
		s1+=chr(0xf6) # scale-y     -10
		s1+=chr(0)
		s1+=self.stitches[colorindex]  # stitch-run
		s1+=chr(0)

		# thread_len=len(self.stitches[colorindex])+len(thread_description) # is that full length ?
		thread_len=len(s1) # is that full length ?
		s+=int2str(thread_len,4)  # 4 bytes thread-len bytes to next thread
		s+=s1
		
		#print "mkstitch:",colorindex,"strlen=",len(s)
		self.embroidery_len+=len(s)
		return s
		
	def mkfileheader(self):
		self.header = "%vsm%"+chr(0)
		self.header+=n_wstr(self.producer)
		# Embroidery Summary-details ***
		# self.embroidery_len=1000  # TODO: replace this fake nr, calculate size
		self.header +=chr(0)+chr(2)+chr(0)   # tag: embroidery-summary packet
		self.header +=int2str ( self.embroidery_len,4 ) # 4 bytes
		self.header +=n_wstr(self.settings) # N-WStr human readable debugging notes
		
		extent_right=self.max_x*100 # count in moveto lineto
		extent_top=self.max_y*100
		extent_left=self.min_x*100
		extent_bottom=self.min_y*100
		# stitch_time_count=2001
		
		thread_change_count=self.cnt;
		hoop_left=extent_left #  hoop is the physical frame, holding the fabric
		hoop_right=extent_right
		hoop_top=extent_top
		hoop_bottom=extent_bottom
		
		hoop_width=abs(extent_right-extent_left)
		hoop_height=abs(extent_bottom-extent_top)
		self.centre_x=(extent_right+extent_left)/2
		self.centre_y=(extent_bottom+extent_top)/2
		
		hoop_left=extent_left-self.centre_x # hoop is the physical frame, holding the fabric
		hoop_right=extent_right-self.centre_x
		hoop_top=extent_top-self.centre_y
		hoop_bottom=extent_bottom-self.centre_y
		
		
		self.header += int2str(extent_right,4) # 4 bytes  right edge of stitching in um starting from 0,0
		self.header += int2str(extent_top,4) # 4 bytes
		self.header += int2str(extent_left,4) # 4 bytes
		self.header += int2str(extent_bottom,4) # 4 bytes
		self.header += int2str(self.stitch_time_count,4) # 4 bytes  time estimate in stitches
		self.header += int2str(thread_change_count,2) # 2 bytes
		

		
		self.header +=chr(12)  # unknown = 12
		self.header +=chr(0)  # unknown = 1 may be hoop-count
		self.header +=chr(1)  # unknown = 1 may be hoop-count
		# Hoop-details ***
		self.hoop_len=self.embroidery_len-len(self.header)
		self.header +=chr(0)+chr(3)+chr(0) # tag: embroidery-summary packet
		self.header +=int2str ( self.hoop_len,4) # 4 bytes
		self.header +=int2str ( self.centre_x,4 ) # MicroM	4 bytes   of summary extent above
		self.header +=int2str ( self.centre_y,4 ) # MicroM	4 bytes 
		self.header +=chr(0)+chr(0)+chr(0) # unknown
		self.header +=int2str ( hoop_left,4 ) # MicroM	4 bytes 
		self.header +=int2str ( hoop_right,4 ) # MicroM	4 bytes 
		self.header +=int2str ( hoop_bottom,4 ) # MicroM	4 bytes 
		self.header +=int2str ( hoop_top,4 ) # MicroM	4 bytes 
		self.header +=int2str ( hoop_width,4 ) # MicroM	4 bytes 
		self.header +=int2str ( hoop_height,4 ) # MicroM	4 bytes 
		self.header +=n_wstr(self.settings) # second copy of settings string  N-WStr human readable debugging notes 
		self.header +=chr(100)  # unknown 
		self.header +=chr(100)  # unknown 
		self.header +=int2str (4096,4)  # 4 bytes unknown 
		self.header +=int2str (0,4)  # 4 bytes unknown 
		self.header +=int2str (0,4)  # 4 bytes unknown 
		self.header +=int2str (4096,4)  # 4 bytes unknown 
		self.header +="xxPP"
		self.header +=chr(1)+chr(0)  # 2 v6i 3 baiti ????????
		self.header +=n_wstr(self.producer)
		self.header += int2str(thread_change_count,2) # 2 bytes

		
		
		
		
		
	def linerel(self,dx,dy,long):
		#dx=clamp(dx) # -127..127
		#dy=clamp(dy)
		dx,dy=clamp2(dx,dy,long)
		ddx=dx
		ddy=-dy # Y negative
		if ddx<0: ddx+=256
		if ddy<0: ddy+=256
		if abs(dx)+abs(dy) >= self.min_stitch_len: # eliminate too short stitches (they damage fabric)
			self.stitches[self.cnt-1]+=chr(ddx)+chr(ddy) 
			self.stitch_time_count+=1
			self.posx+=dx
			self.posy+=dy
			self.total_displacement_x+=dx
			self.total_displacement_y+=dy
		
	def minmax(self,x,y): # collect min,max coordinates
		if self.posx==None:
			self.posx=x
			self.posy=y
		self.max_x=max(self.max_x,x)
		self.max_y=max(self.max_y,y)
		self.min_x=min(self.min_x,x)
		self.min_y=min(self.min_y,y)
		self.endx[self.cnt-1]=x*100
		self.endy[self.cnt-1]=y*100
		if self.startx[self.cnt-1]==None: # first move in new thread goes into startx,starty
			self.startx[self.cnt-1]=x*100
			self.starty[self.cnt-1]=y*100

	def lineto(self,x,y,long=0):
		if self.posx==None:
			self.moveto(x,y)
			return
		self.minmax(x,y)
		dx=x-self.posx
		dy=y-self.posy
		#if dx!=0 or dy!=0:
		if abs(dx) + abs(dy) >= self.min_stitch_len:
			self.linerel(dx,dy,long)
			self.lineto(x,y,long) # go recursive

		#self.stitches[self.cnt-1]+=int2str(x,1)+int2str(y,1)
		#self.stitch_time_count+=1
		# cnt does increment when new color starts
		# self.lines+=int2str(x,1) 
		#self.lines+=int2str(y,1)

	
	def moveto(self,x,y):
		self.minmax(x,y)
		
		#self.lineto(x,y) # DEBUG only
		#return
		dx=x-self.posx
		dy=y-self.posy
		#dy=-dy # Y negative
		if self.startx[self.cnt-1]==None: # first move in new thread goes into startx,starty
			self.startx[self.cnt-1]=x*100
			self.starty[self.cnt-1]=y*100
			#self.posx=x
			#self.posy=y
		#else:
		
		#if abs(dx)<128 and abs(dy)<128:
		#	self.lineto(x,y)
		#	return
		
		self.posx=x
		self.posy=y
		#self.stitches[self.cnt-1]+=chr(128)+chr(3) # cut ?
		#if s_count<1:  #  0x80 01 xx yy 0x80 02
		self.stitches[self.cnt-1]+= chr(128) + chr(1) + int2str(dx,2) + int2str(dy,2) + chr(128)+ chr(2) # jump
		self.stitch_time_count+=1
		#self.stitches[self.last]+=int2str(x,1) 
		#self.stitches[self.last]+=int2str(y,1)


	def setcolor(self,htmlcolor): # todo:  setcolor(self,htmlcolor,colorcode=0)   optional colorcode: 4 digit code
		self.cnt+=1

		self.posx=None # for 4d embroidery.  for artsizer skip this
		self.posy=None
		
		self.stitches.append("")
		self.startx.append(None)
		self.starty.append(None)
		self.endx.append(None)
		self.endy.append(None)
		self.colors.append(htmlcolor)
		#self.startx[self.cnt-1]=None
		#self.starty[self.cnt-1]=None
		#self.headers[self.last]=""
		#print "colorcnt=[",self.cnt,"]",htmlcolor,"--"
		

	def flush(self,fname):   # output the buffers and close a file
		f=open(fname,"wb")
		# self.try_sort_by_color() # todo: create function. merge stitches with same color
		tmpheader=[]
		for r in xrange(self.cnt):
			# todo: create color header
			tmpheader.append(self.mkstitch(r))
			#tmpheader=self.mkcolorheader(self.colors[r])
			# f.write(tmpheader) # header (stitchheaders stitches)
			# self.outcolorheader(f) # alternate way
			#f.write(self.headers[r]) # header (stitchheaders stitches)
			#f.write(self.stitches[r])
			# print "r=",r,"col=",self.colors[r]," last=",self.cnt,"**"
		# for r in tmpheader: self.embroidery_len+=len(r)
		# print "emb_len=",hex(self.embroidery_len)
		self.mkfileheader()
		f.write(self.header)
		for r in tmpheader: f.write(r)
		f.close()


	def flush_str(self):   # output the buffers and close a file
		tmpheader=[]
		for r in xrange(self.cnt):
			tmpheader.append(self.mkstitch(r))
		self.mkfileheader()
		s=self.header
		for r in tmpheader: s+=r
		return s




