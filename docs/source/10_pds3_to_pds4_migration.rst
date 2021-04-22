Mapping SPICE PDS3 docs and catalogs to PDS4
==============================================================================


      aareadme.htm           --> document/spiceds_v*.html
      aareadme.txt           --> ***discard***
      errata.txt             --> document/spiceds_v*.html (errata section)
      voldesc.cat            --> ***discard***

      catalog/catinfo.txt    --> document/spiceds_v*.html
      catalog/insthost.cat   --> ***discard***, pointer to context product
      catalog/mission.cat    --> ***discard***, pointer to context product
      catalog/person.cat     --> ***discard***
      catalog/ref.cat        --> document/spiceds_v*.html (references section)
      catalog/release.cat    --> ***discard*** (versioned collections are equivalent to releases)
      catalog/spice_hsk.cat  --> ***discard***
      catalog/spice_inst.cat --> ***discard***
      catalog/spiceds.cat    --> document/spiceds_v*.html (various sections)

      data/ck/ckinfo.txt     --> document/spiceds_v*.html (CK section)
      data/dsk/ckinfo.txt    --> document/spiceds_v*.html (DSK section)
      data/ek/ekinfo.txt     --> document/spiceds_v*.html (EK section)
      data/fk/fkinfo.txt     --> document/spiceds_v*.html (FK section)
      data/ik/ikinfo.txt     --> document/spiceds_v*.html (IK section)
      data/lsk/lskinfo.txt   --> document/spiceds_v*.html (LSK section)
      data/pck/pckinfo.txt   --> document/spiceds_v*.html (PCK section)
      data/sclk/sclkinfo.txt --> document/spiceds_v*.html (SCLK section)
      data/spk/spkinfo.txt   --> document/spiceds_v*.html (SPK section)

      document/docinfo.txt   --> document/spiceds_v*.html
      document/lblinfo.txt   --> ***discard***
      document/onlabels.txt  --> ***discard***
      document/<>/<>info.txt --> document/spiceds_v*.html

      extras/extrinfo.txt    --> document/spiceds_v*.html
      extras/<>/<>info.txt   --> document/spiceds_v*.html

      index/indxinfo.txt     --> document/spiceds_v*.html
      index/checksum.lbl     --> miscellaneous/checksum/checksum_v???.xml
      index/checksum.tab     --> miscellaneous/checksum/checksum_v???.tab
      index/index.lbl        --> ***discard***
      index/index.tab        --> ***discard***

      software/softinfo.txt  --> document/spiceds_v*.html (software section)