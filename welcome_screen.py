
def gen():
    print('before first yield')
     
    yield
    print('after first yield')
cycle = gen()

cycle