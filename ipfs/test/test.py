


class A(object):
    def __call__(self, prefix):
        def func(msg):
            print prefix+msg
        return func

class B(object):
    def __init__(self):
        self.a = A()

    def __getattribute__(self, name):
        res = object.__getattribute__(self, name)
        return res('hello ')

b = B()
b.a('world')
