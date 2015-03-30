

class PrefVar(object):


    def __init__(self, name = None, default = None, choices = None, comment = None, varType = str, value = None):

        self.name = name
        self.default = default
        self.choices = choices
        self.comment = comment
        self.varType = varType
        self.value = value

    def __repr__(self):
        return '<PrefVar(name: %s, value: %s, default: %s)>' % (self.name, self.value, self.default)
