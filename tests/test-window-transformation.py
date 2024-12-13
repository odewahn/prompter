def transformation_window_split(b, **kwargs):
    N = kwargs.get("N", 1000)
    OVERLAP = kwargs.get("OVERLAP", 0.1)
    STEP = int(N * (1 - OVERLAP))
    res = []
    tokens = b.split()
    for i in range(0, len(tokens), STEP):
        res.append(" ".join(tokens[i : i + N]))
    return res


data = "abcdefghijklmnopqrstuvwxyz0123456789"

# Convert data to an array of bytes
arr = []
for c in data:
    arr.append(c)
data = " ".join(arr)

transformd = transformation_window_split(data, N=10, OVERLAP=0.2)
for t in transformd:
    print(t)
