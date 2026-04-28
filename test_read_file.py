filename = "G:\\Gent\\AWG\\EDG\\grating_points_huannan.txt"
with open(filename, "r") as f:
    for line in f:
        data = line.split('\t')
        print(data)
