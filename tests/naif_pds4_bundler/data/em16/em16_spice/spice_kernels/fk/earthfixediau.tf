
EARTH_FIXED/IAU_EARTH Frame Connection Kernel for New Norcia
============================================================

Updated:                    2004 March 22 01:03:00 PDT (NJB)

   Descriptive comments were added.

Creation date:              2003 June 24 04:22:00 PDT
Created by:                 Nat Bachman (JPL/NAIF)

This kernel associates the IAU_EARTH frame with the EARTH_FIXED
reference frame alias.  Loading this kernel together
with a kernel whose data are relative to the EARTH_FIXED frame
(for example, an SPK or topocentric frame kernel for tracking stations)
allows the SPICE system to treat that kernel's data as though
they were relative to the IAU_EARTH frame.

This kernel normally should be loaded together with a text PCK file
providing earth rotation data.

For high-accuracy work, the ITRF93 frame should be used
rather than the IAU_EARTH frame, and the kernel EARTHFIXEDITRF93.TF
should be used in place of this one to associate the alias
EARTH_FIXED with the ITRF93 frame.

\begindata

TKFRAME_EARTH_FIXED_RELATIVE = 'IAU_EARTH'
TKFRAME_EARTH_FIXED_SPEC     = 'MATRIX'
TKFRAME_EARTH_FIXED_MATRIX   = ( 1   0   0
                                 0   1   0
                                 0   0   1 )

\begintext
