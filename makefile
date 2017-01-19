embroider.tgz: makefile index.html embroider.py embroider.inx embroider_params.py embroider_params.inx images/draft1.jpg images/draft2.jpg images/shirt.jpg PyEmb.py
	ln -fs embroider .
	tar czf $@ $^
