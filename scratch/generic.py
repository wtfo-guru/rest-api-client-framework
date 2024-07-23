

def check(status_code: int) -> None:
    if not 200 <= status_code < 400:
        print("{0} => bad status code".format(status_code))
    else:
        print("{0} => ok".format(status_code))

check(199)
check(200)
check(310)
check(400)
check(401)
