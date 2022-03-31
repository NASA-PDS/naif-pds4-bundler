
EARTH_FIXED/ITRF93 Frame Connection Kernel for New Norcia
============================================================

Updated:                    2004 March 22 01:04:00 PDT (NJB)

   Descriptive comments were added.

Creation date:              2003 June 24 04:22:00 PDT
Created by:                 Nat Bachman (JPL/NAIF)

This kernel associates the ITRF93 frame with the EARTH_FIXED
reference frame alias.  Loading this kernel together
with a kernel whose data are relative to the EARTH_FIXED frame
(for example, an SPK or topocentric frame kernel for tracking stations)
allows the SPICE system to treat that kernel's data as though
they were relative to the ITRF93 frame.

This kernel normally should be loaded together with a binary PCK file
providing earth rotation data.

For low-accuracy work, the IAU_EARTH frame may be used
rather than the ITRF93 frame.  The kernel EARTHFIXEDIAU.TF
should be used in place of this one to associate the alias
EARTH_FIXED with the IAU_EARTH frame.

\begindata

TKFRAME_EARTH_FIXED_RELATIVE = 'ITRF93'
TKFRAME_EARTH_FIXED_SPEC     = 'MATRIX'
TKFRAME_EARTH_FIXED_MATRIX   = ( 1   0   0
                                 0   1   0
                                 0   0   1 )

\begintext
