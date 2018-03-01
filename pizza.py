import sys
sys.setrecursionlimit(10000000)
MAX_INT = sys.maxsize

def print_output(slices, ofs_r = 0, ofs_c = 0):
    print (len(slices))
    for r0, c0, rN, cN in slices:
        print('{} {} {} {}'.format(ofs_r + r0, ofs_c + c0, ofs_r + rN - 1, ofs_c + cN - 1))


def show_slicing(pizza, slices):
    def slice_idx(slices, i, j):
        for ix in range(len(slices)):
            if slices[ix] is not None:
                r0, c0, rN, cN = slices[ix]
                if i >= r0 and i < rN and j >= c0 and j < cN:
                    return ix
        return -1

    R = len(pizza)
    C = len(pizza[0])

    for i in range(R):
        for j in range(C):
            print('{:10n}|{}'.format(slice_idx(slices, i, j), pizza[i][j]), end='')
            #print('{:10n}'.format(slice_idx(slices, i, j)), end='')

        print(end='\n')

    print()


class Cache:
    def __init__(self):
        self.cache = {}

    def make_key(self, r0, c0, rN, cN):
        key = '{} {} {} {}'.format(r0, c0, rN, cN)
        return key

    def set(self, r0, c0, rN, cN, val):
        key = self.make_key(r0, c0, rN, cN)
        self.cache[key] = val

    def get(self, r0, c0, rN, cN):
        key = self.make_key(r0, c0, rN, cN)
        if key in self.cache.keys():
            return self.cache[key]
        else:
            return None


class SliceChecker:
    def __init__(self, pizza, L, H):
        # calculate ingredients
        R = len(pizza)
        C = len(pizza[0])

        row_template = [0] * C
        tc = [row_template[:] for x in range(R)]  # tomato prefix count
        mc = [row_template[:] for x in range(R)]  # mashroom prefix count
        mtcount = {'M': 0, 'T': 0}

        for i in range(R):
            for j in range(C):
                mtcount[pizza[i][j]] += 1

                tc[i][j] = mtcount['T']
                mc[i][j] = mtcount['M']
                if i > 0:
                    tc[i][j] -= tc[i - 1][C - 1] - tc[i - 1][j]
                    mc[i][j] -= mc[i - 1][C - 1] - mc[i - 1][j]

        self.mc = mc
        self.tc = tc

        self.R = R
        self.C = C
        self.H = H
        self.L = L

        self.generate_slices()

        self.pizza = pizza

    def generate_slices(self):
        self.slices = [(1, 1)]  # "slice" is tuple (width, height). "waste of 1" is first slice

        rt = [-1] * (self.H + 1)
        self.slice_ids = [rt[:] for x in range(self.H + 1)]

        self.slice_ids[1][1] = 0

        for i in range(1, self.H + 1):
            for j in range(1, self.H + 1):
                if  self.L * 2 <= i * j <= self.H :
                    self.slices += [(i, j)]

        self.slices.sort(key = lambda this: this[0] * this[1], reverse = True)

        i = 0
        for w, h in self.slices:
            self.slice_ids[w][h] = i
            i += 1

    def lookup_slice(self, h, w):
        return self.slice_ids[h][w]

    def is_ok(self, r0, c0, R, C):
        if R * C > self.H:
            return False

        rN = r0 + R
        cN = c0 + C

        mc = self.mc[rN - 1][cN - 1]
        tc = self.tc[rN - 1][cN - 1]

        if r0 > 0:
            mc -= self.mc[r0 - 1][cN - 1]
            tc -= self.tc[r0 - 1][cN - 1]

        if c0 > 0:
            mc -= self.mc[rN - 1][c0 - 1]
            tc -= self.tc[rN - 1][c0 - 1]

        if r0 > 0 and c0 > 0:
            mc += self.mc[r0 - 1][c0 - 1]
            tc += self.tc[r0 - 1][c0 - 1]

        if mc >= self.L and tc >= self.L:
            return True
        else:
            return False

    def ok_slices(self, r0, c0, R, C):
        # ok_slices should not be bigger then pizza (self.R,C) or available space (R,C) BUT seems R,C includes 1st requirement
        R = min(self.R - r0, R)
        C = min(self.C - c0, C)

        if R == 0 or C == 0:
            return []

        return [[h, w] for h, w in self.slices if
                h <= R and w <= C and self.is_ok(r0, c0, h, w) or (h == 1 and w == 1)]

    def restore_slices(self, slices, waste):
        def traverse_slices(r0, c0, rN, cN):
            if slices.get(r0, c0, rN, cN) is not None:
                si = slices.get(r0, c0, rN, cN)

                if si == [None]:
                    return []  # when out of bounds

                h, w = self.slices[si]

                if w == 1 and h == 1:  # 1 x 1 should not be considered a slice
                    res = []
                else:
                    res = [[r0, c0, r0 + h, c0 + w]]

                wV = [waste.get(r0, c0 + w, rN, cN), waste.get(r0 + h, c0, rN, c0 + w)]
                wasteV = sum([w for w in wV if w is not None])

                wH = [waste.get(r0, c0 + w, r0 + h, cN), waste.get(r0 + h, c0, rN, cN)]
                wasteH = sum([w for w in wH if w is not None])

                if wasteV < wasteH:
                    res += traverse_slices(r0, c0 + w, rN, cN) + traverse_slices(r0 + h, c0, rN, c0 + w)
                else:
                    res += traverse_slices(r0, c0 + w, r0 + h, cN) + traverse_slices(r0 + h, c0, rN, cN)

                return res
            return []  # is it ok?

        return traverse_slices(0, 0, self.R, self.C)


def calculate_min_waste(pizza, L, H, R, C):
    def calculate_min_waste_dp(r0, c0, rN, cN):
        R = rN - r0
        C = cN - c0

        if waste_cache.get(r0, c0, rN, cN) is not None:
            return waste_cache.get(r0, c0, rN, cN)

        min_waste = MAX_INT
        min_slice = None

        ok_slices = slice_checker.ok_slices(r0, c0, R, C)
        if ok_slices == []:
            slice_cache.set(r0, c0, rN, cN, None)
            waste_cache.set(r0, c0, rN, cN, 0)

            return 0

        for h, w in ok_slices:
            slice_id = slice_checker.lookup_slice(h, w)

            wasteV = calculate_min_waste_dp(r0, c0 + w, rN, cN) + calculate_min_waste_dp(r0 + h, c0, rN,  c0 + w)
            wasteH = calculate_min_waste_dp(r0, c0 + w, r0 + h, cN) + calculate_min_waste_dp(r0 + h, c0, rN, cN)

            waste = min(wasteV, wasteH)

            if (h == 1 and w == 1):
                waste += 1

            if waste < min_waste:
                min_slice = slice_id
                min_waste = waste

            if min_waste == 0:
                break

        slice_cache.set(r0, c0, rN, cN, min_slice)
        waste_cache.set(r0, c0, rN, cN, min_waste)

        return waste_cache.get(r0, c0, rN, cN)

    slice_checker = SliceChecker(pizza, L, H)

    waste_cache = Cache()
    slice_cache = Cache()

    w = calculate_min_waste_dp(0, 0, R, C)

    s = slice_checker.restore_slices(slice_cache, waste_cache)

    return s, w

