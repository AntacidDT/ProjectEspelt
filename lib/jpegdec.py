import struct
import math


class JPEGDecoder:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.quant_tables = {}
        self.huff_tables = {}
        self.scan_data = None
        self.sof_info = None

    def decode(self, filename, tft, x=0, y=0, max_w=None, max_h=None):
        with open(filename, 'rb') as f:
            data = f.read()

        if data[:2] != b'\xff\xd8':
            raise ValueError('Not a JPEG file')

        self._parse(data)

        if max_w and max_h:
            scale_x = max_w / self.width
            scale_y = max_h / self.height
            scale = min(scale_x, scale_y)
            out_w = int(self.width * scale)
            out_h = int(self.height * scale)
        else:
            out_w = self.width
            out_h = self.height

        pixels = self._decode_scan()

        self._render_to_tft(tft, pixels, x, y, out_w, out_h)

        return out_w, out_h

    def _parse(self, data):
        i = 2
        while i < len(data) - 1:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker == 0x00:
                i += 2
                continue
            if marker in (0xD8, 0xD9):
                break
            if marker == 0xDA:
                self._parse_sos(data, i)
                return
            length = struct.unpack('>H', data[i + 2:i + 4])[0]
            if marker == 0xC0:
                self._parse_sof(data, i + 4, length - 2)
            elif marker == 0xC4:
                self._parse_dht(data, i + 4, length - 2)
            elif marker == 0xDB:
                self._parse_dqt(data, i + 4, length - 2)
            i += 2 + length

    def _parse_sof(self, data, offset, length):
        precision = data[offset]
        self.height = struct.unpack('>H', data[offset + 1:offset + 3])[0]
        self.width = struct.unpack('>H', data[offset + 3:offset + 5])[0]
        num_components = data[offset + 5]
        self.sof_info = {
            'precision': precision,
            'num_components': num_components,
            'components': []
        }
        off = offset + 6
        for _ in range(num_components):
            comp_id = data[off]
            sampling = data[off + 1]
            quant_table = data[off + 2]
            self.sof_info['components'].append({
                'id': comp_id,
                'sampling': sampling,
                'quant_table': quant_table
            })
            off += 3

    def _parse_dht(self, data, offset, length):
        off = offset
        while off < offset + length:
            info = data[off]
            table_class = (info >> 4) & 0x0F
            table_id = info & 0x0F
            bits = list(data[off + 1:off + 17])
            num_symbols = sum(bits)
            symbols = list(data[off + 17:off + 17 + num_symbols])
            key = (table_class, table_id)
            self.huff_tables[key] = {'bits': bits, 'symbols': symbols}
            off += 17 + num_symbols

    def _parse_dqt(self, data, offset, length):
        off = offset
        while off < offset + length:
            info = data[off]
            table_id = info & 0x0F
            precision = (info >> 4) & 0x0F
            table = []
            for j in range(64):
                if precision == 0:
                    table.append(data[off + 1 + j])
                else:
                    table.append(struct.unpack('>H', data[off + 1 + j * 2:off + 3 + j * 2])[0])
            self.quant_tables[table_id] = table
            off += 1 + 64 * (1 + precision)

    def _parse_sos(self, data, offset):
        length = struct.unpack('>H', data[offset + 2:offset + 4])[0]
        num_components = data[offset + 4]
        components = []
        off = offset + 5
        for _ in range(num_components):
            comp_id = data[off]
            dc_table = (data[off + 1] >> 4) & 0x0F
            ac_table = data[off + 1] & 0x0F
            components.append({'id': comp_id, 'dc_table': dc_table, 'ac_table': ac_table})
            off += 2
        spectral_start = data[off]
        spectral_end = data[off + 1]
        approx_high = (data[off + 2] >> 4) & 0x0F
        approx_low = data[off + 2] & 0x0F

        self.scan_data = data[offset + 4 + 1 + num_components * 2 + 3:]

    def _decode_scan(self):
        if not self.scan_data or not self.sof_info:
            raise ValueError('No scan data found')

        num_components = self.sof_info['num_components']
        mcu_w = 8
        mcu_h = 8
        h_max = 1
        v_max = 1

        for comp in self.sof_info['components']:
            sampling = comp['sampling']
            h = (sampling >> 4) & 0x0F
            v = sampling & 0x0F
            if h > h_max:
                h_max = h
            if v > v_max:
                v_max = v

        mcus_x = (self.width + mcu_w * h_max - 1) // (mcu_w * h_max)
        mcus_y = (self.height + mcu_h * v_max - 1) // (mcu_h * v_max)

        pixels = bytearray(self.width * self.height * 2)

        bit_pos = [0]
        dc_values = [0] * num_components

        quant_map = {}
        for i, comp in enumerate(self.sof_info['components']):
            quant_map[i] = self.quant_tables[comp['quant_table']]

        for mcu_y in range(mcus_y):
            for mcu_x in range(mcus_x):
                blocks = []
                for comp_idx in range(num_components):
                    comp = self.sof_info['components'][comp_idx]
                    sampling = comp['sampling']
                    h_samp = (sampling >> 4) & 0x0F
                    v_samp = sampling & 0x0F

                    for by in range(v_samp):
                        for bx in range(h_samp):
                            block = self._decode_block(
                                bit_pos, dc_values, comp_idx,
                                comp['dc_table'], comp['ac_table']
                            )
                            quant = quant_map[comp_idx]
                            block = self._dequantize(block, quant)
                            block = self._idct(block)
                            blocks.append((block, bx, by, h_samp, v_samp))

                self._render_mcu(pixels, blocks, mcu_x, mcu_y,
                                 h_max, v_max, mcu_w, mcu_h, num_components)

        return pixels

    def _decode_block(self, bit_pos, dc_values, comp_idx, dc_table_id, ac_table_id):
        block = [0] * 64

        dc_key = (0, dc_table_id)
        dc_table = self.huff_tables.get(dc_key, {'bits': [0]*16, 'symbols': []})
        bits_read = self._read_huffman(bit_pos, dc_table)
        if bits_read > 0:
            diff = self._read_bits(bit_pos, bits_read)
            if diff < (1 << (bits_read - 1)):
                diff -= (1 << bits_read) - 1
        else:
            diff = 0
        dc_values[comp_idx] += diff
        block[0] = dc_values[comp_idx]

        ac_key = (1, ac_table_id)
        ac_table = self.huff_tables.get(ac_key, {'bits': [0]*16, 'symbols': []})

        pos = 1
        while pos < 64:
            ac_info = self._read_huffman(bit_pos, ac_table)
            if ac_info == 0:
                break
            run = (ac_info >> 4) & 0x0F
            size = ac_info & 0x0F
            pos += run
            if pos >= 64:
                break
            if size > 0:
                val = self._read_bits(bit_pos, size)
                if val < (1 << (size - 1)):
                    val -= (1 << size) - 1
                block[pos] = val
            pos += 1

        return block

    def _read_huffman(self, bit_pos, table):
        bits_str = ''
        for length in range(1, 17):
            if bit_pos[0] // 8 >= len(self.scan_data):
                return 0
            byte_idx = bit_pos[0] // 8
            bit_idx = 7 - (bit_pos[0] % 8)
            bit = (self.scan_data[byte_idx] >> bit_idx) & 1
            bits_str += str(bit)
            bit_pos[0] += 1

            symbols = table.get('symbols', [])
            bit_counts = table.get('bits', [])
            symbol_idx = 0
            for l in range(length):
                symbol_idx += bit_counts[l]

            for idx, sym in enumerate(symbols):
                check_str = ''
                temp_pos = bit_pos[0] - length
                for _ in range(length):
                    bi = 7 - (temp_pos % 8)
                    byte_i = temp_pos // 8
                    if byte_i < len(self.scan_data):
                        check_str += str((self.scan_data[byte_i] >> bi) & 1)
                    temp_pos += 1
                if check_str == bits_str:
                    bit_pos[0] = bit_pos[0]
                    return sym

        return 0

    def _read_bits(self, bit_pos, num_bits):
        val = 0
        for _ in range(num_bits):
            if bit_pos[0] // 8 >= len(self.scan_data):
                break
            byte_idx = bit_pos[0] // 8
            bit_idx = 7 - (bit_pos[0] % 8)
            bit = (self.scan_data[byte_idx] >> bit_idx) & 1
            val = (val << 1) | bit
            bit_pos[0] += 1
        return val

    def _dequantize(self, block, quant):
        return [block[i] * quant[i] for i in range(64)]

    def _idct(self, block):
        result = [0.0] * 64
        for u in range(8):
            for v in range(8):
                cu = 1.0 / math.sqrt(2) if u == 0 else 1.0
                cv = 1.0 / math.sqrt(2) if v == 0 else 1.0
                s = 0.0
                for x in range(8):
                    for y in range(8):
                        s += cu * cv * block[x * 8 + y] * \
                             math.cos((2 * x + 1) * u * math.pi / 16) * \
                             math.cos((2 * y + 1) * v * math.pi / 16)
                result[u * 8 + v] = s / 4.0

        final = [0] * 64
        for i in range(64):
            val = int(result[i] + 128)
            final[i] = max(0, min(255, val))
        return final

    def _render_mcu(self, pixels, blocks, mcu_x, mcu_y,
                    h_max, v_max, mcu_w, mcu_h, num_components):
        mcu_base_x = mcu_x * mcu_w * h_max
        mcu_base_y = mcu_y * mcu_h * v_max

        if num_components == 1:
            block_data = blocks[0][0]
            for by in range(mcu_h):
                for bx in range(mcu_w):
                    px = mcu_base_x + bx
                    py = mcu_base_y + by
                    if px >= self.width or py >= self.height:
                        continue
                    val = max(0, min(255, block_data[by * 8 + bx]))
                    r5 = val >> 3
                    g6 = val >> 2
                    b5 = val >> 3
                    color = (r5 << 11) | (g6 << 5) | b5
                    idx = (py * self.width + px) * 2
                    pixels[idx] = (color >> 8) & 0xFF
                    pixels[idx + 1] = color & 0xFF
            return

        y_block = blocks[0][0]
        cb_block = blocks[1][0] if len(blocks) > 1 else [128] * 64
        cr_block = blocks[2][0] if len(blocks) > 2 else [128] * 64

        for by in range(mcu_h):
            for bx in range(mcu_w):
                px = mcu_base_x + bx
                py = mcu_base_y + by
                if px >= self.width or py >= self.height:
                    continue

                y_val = y_block[by * 8 + bx]
                cb = cb_block[by * 8 + bx] - 128
                cr = cr_block[by * 8 + bx] - 128

                r = int(y_val + 1.402 * cr)
                g = int(y_val - 0.344 * cb - 0.714 * cr)
                b = int(y_val + 1.772 * cb)

                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))

                r5 = r >> 3
                g6 = g >> 2
                b5 = b >> 3
                color = (r5 << 11) | (g6 << 5) | b5

                idx = (py * self.width + px) * 2
                pixels[idx] = (color >> 8) & 0xFF
                pixels[idx + 1] = color & 0xFF

    def _render_to_tft(self, tft, pixels, x, y, out_w, out_h):
        tft._set_window(x, y, x + out_w - 1, y + out_h - 1)
        tft._dc(1)
        tft._cs(0)
        chunk_size = 1024
        for i in range(0, len(pixels), chunk_size):
            tft._spi.write(bytes(pixels[i:i + chunk_size]))
        tft._cs(1)
