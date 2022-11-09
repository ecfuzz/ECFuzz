import re

if __name__ == "__main__":
    file = "fuzzer.log"
    mx =0
    with open(file) as f:
        while True:
            line = f.readline()
            if not line:
                break
            res =  re.findall(r'with running time .* failed',line)
            if len(res):
                # print(res)
                ls = res[0].split(' ')
                # print(ls)
                mx = max(float(ls[3]),mx)
    print(mx)