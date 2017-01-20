PREFIX ?= ~/.config/inkscape/extensions

embroider.tgz: makefile index.html embroider.py embroider.inx embroider_params.py embroider_params.inx reorder.py reorder.inx svg2emb.inx PyEmb.py README.md TODO images/draft1.jpg images/draft2.jpg images/shirt.jpg
	tar czf $@ $^

install:
	ln -fs $(PWD)/* $(PREFIX)

clean:
	git clean -xi
