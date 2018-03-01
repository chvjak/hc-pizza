import datetime
from pizza import calculate_min_waste
from pizza import print_output
from pizza import show_slicing
from pizza import SliceChecker
from multiprocessing import Pool


def slice(args):
    pizza, L, H  = args
    print(datetime.datetime.now())
    slices, waste = calculate_min_waste(pizza, L, H, len(pizza), len(pizza[0]))
    print(waste, len(slices))
    print(datetime.datetime.now())

    return slices


if __name__ == '__main__':
    #f = open('pizza-example.txt')
    #f = open('pizza-small.txt')
    #f = open('pizza-medium.txt')
    f = open('pizza-big.txt')

    def input():
        return f.readline()


    # R x C - pizza size
    # L - min ingredient count
    # H - max pizza slice size
    R, C, L, H  = [int(x) for x in input().strip().split()]

    pizza = [None] * R
    for i in range(R):
        pizza[i] = input().strip()

    div_R = 5
    div_C = 5

    step_R = R // div_R
    step_C = C // div_C

    slicer_array = [None] * (div_R * div_C)
    for i in range(div_R):
        for j in range(div_C):
            ofs_r = i * step_R
            ofs_c = j * step_C

            small_pizza  = [r[ofs_c:ofs_c + step_C] for r in pizza[ofs_r:ofs_r + step_R]]

            slicer_array[i * div_C + j] = (small_pizza, L, H)

    p = Pool(div_R * div_C)
    slices = p.map(slice, slicer_array)

    merged_slices = []
    miss_count = 0
    for i in range(div_R):
        for j in range(div_C):

            ofs_r = i * step_R
            ofs_c = j * step_C
            print(ofs_r, ofs_c)

            small_pizza = slicer_array[i * div_C + j][0]

            print(miss_count)
            merged_slices += [[r0 + ofs_r, c0 + ofs_c, rN + ofs_r, cN + ofs_c] for r0, c0, rN, cN in slices[i * div_C + j]]


    #show_slicing(pizza, merged_slices)
    print_output(merged_slices)