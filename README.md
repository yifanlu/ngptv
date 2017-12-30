ngptv
=====
This is an attempt at making an HDMI adapter for the Vita. It does not work 
because the ADV7533 does not support the auto clock stopping that the Vita uses 
to save battery on the MIPI DSI clock. There are two ways of getting it to 
work.

1. Replace the ADV7533 with another part that supports MIPI clock going from 
HS to LP mode when the data lanes are not in use. There are no other DSI to 
HDMI part, but you might get away with stacking a DSI to eDP and eDP to HDMI 
for example. Another way is to use a FPGA and convert the signals manually.
2. Creating some custom part to "filter" the stopped clock to a continuous 
clock. There does not appear to be any off-the-shelf part that does this and 
I've tried looking into re-purposing jitter correctors but they don't work 
because they average out the clock signals instead of locking on to the highest 
frequency.

Both are too much work for me to consider doing, so I will leave this non-
working project as is. Included are two designs. First is ngptv, which is 
supposed to be a small board that fits inside the Vita. Due to the design 
constraints of the ADV7533 (small pitch BGA) which requires > 6 layers and the 
small size requirement of all components, it does not seem feasible for me to 
prototype (too expensive and I don't have the right equipment to assemble).
Additionally, the ADV7533 is a NDA part that requires a HDMI license to buy.

The second design is ngptv lite which is designed to connect directly to a 
[B-LCDAD-HDMI](http://www.st.com/en/development-tools/b-lcdad-hdmi1.html) 
daughterboard. This $30 board contains a ADV7533 and was originally designed to 
work with a ST evaluation board. We instead connect it to the ngptv lite which 
has a microcontroller to interface with ADV7533 as well as a redriver for MIPI 
DSI. Using a 
[FFTP-07-D-03.85-01-N](https://www.samtec.com/products/fftp-07-d-03.85-01-n) 
cable, this connects to a breakout board placed inside the Vita that brings in 
the MIPI DSI signals from the exposed testpoints. The first version lacked the 
redriver, which seemed to still work (to the extent that it works if you 
manually set the Vita's MIPI clock to not use LP mode, which breaks the on 
screen video).

These designs are provided as-is under CC 4.0.
