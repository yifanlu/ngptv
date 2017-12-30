#!/usr/bin/python

# Sequence from https://github.com/xerpi/vita-baremetal-sample/blob/master/src/hdmi.c

import smbus

HDMI_I2C_BUS = 1
HDMI_I2C_ADDR = 0x7A

# Configurable addresses
HDMI_I2C_CEC_ADDR = 0x78

# ADV7533 Main registers
ADV7533_REG_PACKET_ENABLE0 = 0x40
ADV7533_REG_POWER = 0x41
ADV7533_REG_STATUS = 0x42
ADV7533_REG_AVI_INFOFRAME_1 = 0x56
ADV7533_REG_INT_1 = 0x97
ADV7533_REG_HDCP_HDMI_CFG = 0xAF
ADV7533_REG_CEC_I2C_ADDR = 0xE1
ADV7533_REG_POWER2 = 0xD6

ADV7533_PACKET_ENABLE_GC = 0x80

ADV7533_POWER_POWER_DOWN = 0x40

ADV7533_INT1_BKSV = 0x40

ADV7533_STATUS_HPD = 0x40

ADV7533_REG_POWER2_HPD_SRC_MASK = 0xC0
ADV7533_REG_POWER2_HPD_SRC_HPD = 0x40

# ADV7533 CEC registers
ADV7533_REG_CEC_DSI_INTERNAL_TIMING = 0x27

LANES = 2
CLOCK_DIV_BY_LANES = [6, 4, 3]

def hdmi_write(bus, addr, reg, data):
  bus.write_byte_data(addr>>1, reg, data)

def hdmi_read(bus, addr, reg):
  return bus.read_byte_data(addr>>1, reg)

def hdmi_set_bit(bus, addr, reg, bit):
  val = hdmi_read(bus, addr, reg)
  val |= bit
  hdmi_write(bus, addr, reg, val)

def hdmi_clr_bit(bus, addr, reg, bit):
  val = hdmi_read(bus, addr, reg)
  val &= ~bit
  hdmi_write(bus, addr, reg, val)

def hdmi_update_bits(bus, addr, reg, mask, val):
  data = hdmi_read(bus, addr, reg)
  data &= ~mask
  data |= val & mask
  hdmi_write(bus, addr, reg, data)

def main(bus, test, hdcp):
  print "Setting up CEC address"
  hdmi_write(bus, HDMI_I2C_ADDR, ADV7533_REG_CEC_I2C_ADDR, HDMI_I2C_CEC_ADDR)

  print "Waiting for HDMI hot-plug detect"
  while True:
    status = hdmi_read(bus, HDMI_I2C_ADDR, ADV7533_REG_STATUS)
    if ((status & ADV7533_STATUS_HPD) != 0):
      break

  print "Powering up ADV7533"
  hdmi_update_bits(bus, HDMI_I2C_ADDR, ADV7533_REG_POWER, ADV7533_POWER_POWER_DOWN, 0)
  hdmi_update_bits(bus, HDMI_I2C_ADDR, ADV7533_REG_POWER2, ADV7533_REG_POWER2_HPD_SRC_MASK, ADV7533_REG_POWER2_HPD_SRC_HPD)

  print "Sending main config sequence"
  hdmi_write(bus, HDMI_I2C_ADDR, 0x16, 0x20)
  hdmi_write(bus, HDMI_I2C_ADDR, 0x9a, 0xe0)
  hdmi_write(bus, HDMI_I2C_ADDR, 0xba, 0x70)
  hdmi_write(bus, HDMI_I2C_ADDR, 0xde, 0x82)
  hdmi_write(bus, HDMI_I2C_ADDR, 0xe4, 0x40)
  hdmi_write(bus, HDMI_I2C_ADDR, 0xe5, 0x80)

  print "Sending CEC config sequence"
  hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x15, 0xd0)
  hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x17, 0xd0)
  hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x24, 0x20)
  hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x57, 0x11)
  hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x05, 0xc8)

  print "Set number of dsi lanes"
  hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x1C, LANES << 4)

  if (test):
    print "Set pixel clock auto mode"
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x16, 0x00)
  else:
    print "Set pixel clock divider mode"
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x16, CLOCK_DIV_BY_LANES[LANES - 2] << 3)

  if (test):
    htotal, vtotal, hfp, hsw, hbp, vfp, vsw, vbp = 0x672, 0x2EE, 0x6E,  0x28,  0xDC, 5,   5, 0x14;

    print "Horizontal porch params"
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x28, htotal >> 4);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x29, (htotal << 4) & 0xff);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x2a, hsw >> 4);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x2b, (hsw << 4) & 0xff);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x2c, hfp >> 4);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x2d, (hfp << 4) & 0xff);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x2e, hbp >> 4);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x2f, (hbp << 4) & 0xff);

    print "Vertical porch params"
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x30, vtotal >> 4);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x31, (vtotal << 4) & 0xff);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x32, vsw >> 4);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x33, (vsw << 4) & 0xff);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x34, vfp >> 4);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x35, (vfp << 4) & 0xff);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x36, vbp >> 4);
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x37, (vbp << 4) & 0xff);

    print "Enable internal timing generator"
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, ADV7533_REG_CEC_DSI_INTERNAL_TIMING, 0xCB)
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, ADV7533_REG_CEC_DSI_INTERNAL_TIMING, 0x8B)
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, ADV7533_REG_CEC_DSI_INTERNAL_TIMING, 0xCB)
  else:
    print "Disable internal timing generator"
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, ADV7533_REG_CEC_DSI_INTERNAL_TIMING, 0x0B)

  print "GC Packet Enable"
  hdmi_write(bus, HDMI_I2C_ADDR, ADV7533_REG_PACKET_ENABLE0, ADV7533_PACKET_ENABLE_GC)

  print "Down Dither Output Colour Depth - 8 Bit (default)"
  hdmi_write(bus, HDMI_I2C_ADDR, 0x49, 0x00)

  print "Set HDMI/DVI Mode Select = HDMI Mode Enabled - bit 1"
  hdmi_set_bit(bus, HDMI_I2C_ADDR, ADV7533_REG_HDCP_HDMI_CFG, 0x2)

  print "Set Color Depth to 24 Bits/Pixel"
  hdmi_clr_bit(bus, HDMI_I2C_ADDR, 0x4C, 0x0F)
  hdmi_set_bit(bus, HDMI_I2C_ADDR, 0x4C, 0x04)

  print "Set Active Format Aspect Ratio = 16:9 (Center)"
  hdmi_clr_bit(bus, HDMI_I2C_ADDR, ADV7533_REG_AVI_INFOFRAME_1, 0x1F)
  hdmi_set_bit(bus, HDMI_I2C_ADDR, ADV7533_REG_AVI_INFOFRAME_1, 0x2A)

  print "Set V1P2 Enable"
  hdmi_set_bit(bus, HDMI_I2C_ADDR, 0xE4, 0xC0)

  if (test):
    print "Enable test mode"
    hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x55, 0x80)
  else:
    print "Disable test mode"
    hdmi_clr_bit(bus, HDMI_I2C_CEC_ADDR, 0x55, 0x00)

  print "Enable hdmi"
  hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x03, 0x89)

  if (hdcp):
    print "Set HDCP"
    hdmi_write(bus, HDMI_I2C_ADDR, ADV7533_REG_HDCP_HDMI_CFG, 0x96)

    print "Wait for the BKSV flag"
    while True:
      status = hdmi_read(bus, HDMI_I2C_ADDR, ADV7533_REG_INT_1)
      if ((status & ADV7533_INT1_BKSV) != 0):
        break

    print "Clear BKSV interrupt"
    hdmi_write(bus, HDMI_I2C_ADDR, ADV7533_REG_INT_1, (status & ~0xBF) | ADV7533_INT1_BKSV)

  print "Done."

def init(bus):
  print "Setting up CEC address"
  hdmi_write(bus, HDMI_I2C_ADDR, ADV7533_REG_CEC_I2C_ADDR, HDMI_I2C_CEC_ADDR)

def configure(bus, lanes):
  # ADV7533 Power Settings
  print "Power down"
  hdmi_clr_bit(bus, HDMI_I2C_ADDR, 0x41, 0x40)
  print "HPD Override"
  hdmi_set_bit(bus, HDMI_I2C_ADDR, 0xD6, 0xc0)
  print "Gate DSI LP Oscillator and DSI Bias Clock Powerdown"
  hdmi_clr_bit(bus, HDMI_I2C_CEC_ADDR, 0x03, 0x02)
  
  print "Fixed registers that must be set on power-up"
  hdmi_update_bits(bus, HDMI_I2C_ADDR, 0x16, 0x3E, 0x20)
  hdmi_write(bus, HDMI_I2C_ADDR, 0x9A, 0xE0)
  hdmi_update_bits(bus, HDMI_I2C_ADDR, 0xBA, 0xF8, 0x70)
  hdmi_write(bus, HDMI_I2C_ADDR, 0xDE, 0x82)
  
  hdmi_set_bit(bus, HDMI_I2C_ADDR, 0xE4, 0x40)
  hdmi_write(bus, HDMI_I2C_ADDR, 0xE5, 0x80)
  
  hdmi_update_bits(bus, HDMI_I2C_CEC_ADDR, 0x15, 0x30, 0x10)
  hdmi_update_bits(bus, HDMI_I2C_CEC_ADDR, 0x17, 0xF0, 0xD0)
  hdmi_clr_bit(bus, HDMI_I2C_CEC_ADDR, 0x24, 0x10)
  hdmi_set_bit(bus, HDMI_I2C_CEC_ADDR, 0x57, 0x10 | 0x01)
  
  print "Configure the number of DSI lanes"
  hdmi_write(bus, HDMI_I2C_CEC_ADDR, 0x1C, (lanes << 4))
  
  # Setup video output mode
  print "Select HDMI mode"
  hdmi_set_bit(bus, HDMI_I2C_ADDR, 0xAF, 0x02)
  print "HDMI Output Enable"
  hdmi_set_bit(bus, HDMI_I2C_CEC_ADDR, 0x03, 0x80)

  print "GC packet enable"
  hdmi_set_bit(bus, HDMI_I2C_ADDR, 0x40, 0x80)
  print "Input color depth 24-bit per pixel"
  hdmi_update_bits(bus, HDMI_I2C_ADDR, 0x4C, 0x0F, 0x03)
  print "Down dither output color depth"
  hdmi_write(bus, HDMI_I2C_ADDR, 0x49, 0xfc)
  
  print "Internal timing disabled"
  hdmi_clr_bit(bus, HDMI_I2C_CEC_ADDR, 0x27, 0x80)

def show_test_pattern(bus):
  print "Set test pattern"
  hdmi_set_bit(bus, HDMI_I2C_CEC_ADDR, 0x55, 0x80)
  hdmi_set_bit(bus, HDMI_I2C_CEC_ADDR, 0x55, 0xA0)
  print "HDMI Output Enable"
  hdmi_set_bit(bus, HDMI_I2C_CEC_ADDR, 0x03, 0x89)
  print "Select HDMI mode"
  hdmi_set_bit(bus, HDMI_I2C_ADDR, 0xAF, 0x16)

def setup_audio(bus):
  print "HDMI Startup"
  n_value = 6144;
  temp_byte = ((n_value&0xF0000)>>16) & 0xFF
  hdmi_write(bus, HDMI_I2C_ADDR, 0x1, temp_byte);

  temp_byte = ((n_value&0xFF00)>>8) & 0xFF
  hdmi_write(bus, HDMI_I2C_ADDR, 0x2, temp_byte);

  temp_byte = (n_value&0xFF) & 0xFF
  hdmi_write(bus, HDMI_I2C_ADDR, 0x3, temp_byte);

  print "Set SPDIF Enable = SPDIF Enabled"
  hdmi_set_bit(bus, HDMI_I2C_ADDR, 0x0B, 0x80);

  print "Set I2S Enable = I2S Enabled"
  hdmi_set_bit(bus, HDMI_I2C_ADDR, 0x0C, 0x04);

  print "Set I2S Sampling Frequency = 48.0 kHz is 0x20, 44.1Khz is 0x0"
  hdmi_write(bus, HDMI_I2C_ADDR, 0x15, 0x0);

  print "Set Audio Select = SPDIF Input is 0x10, I2S is 0x0"
  hdmi_set_bit(bus, HDMI_I2C_ADDR, 0x0A, 0x00);

def power_up(bus):
  print "Power up"
  hdmi_clr_bit(bus, HDMI_I2C_ADDR, 0x41, 0x40)

if __name__ == "__main__":
  bus = smbus.SMBus(HDMI_I2C_BUS)
  main(bus, 0, 1)
  #init(bus)
  #configure(bus, 2)
  #show_test_pattern(bus)
  #setup_audio(bus)
  #power_up(bus)
