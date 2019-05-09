class DictLikeStruct:
    def __init__(self, entries):
        self.__dict__.update(entries)

    def __str__(self):
        return str(self.__dict__)

    def __contains__(self, k):
        return k in self.__dict__.keys()

    def __getitem__(self, k):
        return self.__dict__[k]

    def __getattr__(self, a):
        if a in self.__dict__:
            return self.__dict__[a]
        raise AttributeError('No such attribute: %s' % a)

    def toDict(self):
        return dict(self.__dict__)
