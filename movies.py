import hashlib
import sys
import os
import urllib

MD5SIZE = 10485760

class Movies:

    def __init__(self):
        self.hexDigest = 0
        self.hexDigestF = 0

    def f(self,z):
	idx = [ 0xe, 0x3,  0x6, 0x8, 0x2 ]
	mul = [   2,   2,    5,   4,   3 ]
	add = [   0, 0xd, 0x10, 0xb, 0x5 ]

	b = []
	for i in xrange(len(idx)):
		a = add[i]
		m = mul[i]
		i = idx[i]

		t = a + int(z[i], 16)
		v = int(z[t:t+2], 16)
		b.append( ("%x" % (v*m))[-1] )

	return ''.join(b)

    def calculateDigest(self, movieName):
        hash = hashlib.md5()
        hash.update(open(movieName).read(MD5SIZE))
        self.hexDigest = hash.hexdigest()
        self.hexDigestF = self.f(self.hexDigest)
        print self.hexDigest
        print self.hexDigestF

    def getTitleFromNapiProjekt(self):
        urlAddr = "http://napiprojekt.pl/unit_napisy/dl.php?l=PL&f="+self.hexDigest+"&t="+self.hexDigestF+"&v=other&kolejka=false&nick=&pass=&napios="+os.name
        open("subtitles.7z","w").write(urllib.urlopen(urlAddr).read())
        
def main():
    instance = Movies()
    instance.calculateDigest(sys.argv[1])
    instance.getTitleFromNapiProjekt()

if __name__ == "__main__":
    main()
