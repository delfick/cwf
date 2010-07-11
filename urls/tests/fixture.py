from urls.section import Site, Section

theTestSite = Site('tester')

sect1 = Section('meh')
sect2 = Section('blah')
sect3 = Section('blip')

theTestSite.add(sect1)
theTestSite.add(sect2, inMenu=True)
theTestSite.add(sect3, base=True)
