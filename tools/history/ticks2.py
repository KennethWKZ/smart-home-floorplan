import sys, json
geo = json.load(open(sys.argv[1]))
import re
# split outline path into subpaths and report short diagonal ones
subs = re.findall(r"M[^M]+", geo["outline"])
diag = []
for s in subs:
    nums = list(map(float, re.findall(r"-?\d+\.?\d*", s)))
    xs, ys = nums[0::2], nums[1::2]
    w, h = max(xs)-min(xs), max(ys)-min(ys)
    if 1 < w < 9 and 1 < h < 9: diag.append((s[:60], round(w,1), round(h,1)))
print(len(subs), "outline subpaths;", len(diag), "short diagonal"); print(diag[:6])
subs = re.findall(r"M[^M]+", geo["furniture"])
d2 = [s[:50] for s in subs if (lambda n: (lambda xs, ys: 2 < max(xs)-min(xs) < 6 and 2 < max(ys)-min(ys) < 6 and abs((max(xs)-min(xs))-(max(ys)-min(ys)))<0.3 and len(n)==4)(n[0::2], n[1::2]))(list(map(float, re.findall(r"-?\d+\.?\d*", s))))]
print(len(d2), "furniture 45deg short strokes", d2[:5])
