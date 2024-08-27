def calc_bowling_score(pins):
    from itertools import accumulate

    pins = list(pins)
    odd = False
    cnts = []
    types = []  # 0特になし、1ストライク、2スペア
    for pin in pins[:-3]:
        odd ^= True
        if odd:
            if pin == 10:
                cnts.append(pin)
                types.append(1)
            else:
                cnts.append(pin)
                types.append(0)
        else:
            if types[-1] == 1:
                continue
            elif cnts[-1] + pin == 10:
                cnts.append(pin)
                types.append(2)
            else:
                cnts.append(pin)
                types.append(0)

    types += [0, 0, 0]
    cnts += pins[-3:]
    first = True
    scores = []
    for i, (type_, cnt) in enumerate(zip(types[:-3], cnts[:-3])):
        if type_ == 1:
            scores.append(cnt + cnts[i + 1] + cnts[i + 2])
        elif first:
            first ^= True
            continue
        else:
            if type_ == 2:
                scores.append(cnts[i - 1] + cnt + cnts[i + 1])
            else:
                scores.append(cnts[i - 1] + cnt)
            first ^= True

    scores.append(sum(pins[-3:]))
    return list(accumulate(scores))
