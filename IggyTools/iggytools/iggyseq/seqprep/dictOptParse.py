from argparse import ArgumentParser


class DictArgumentParser(ArgumentParser):

    def parse_args(self, argv):

        argsNS = ArgumentParser.parse_args(self, argv)

        argsDict = dict( [(name, argsNS.__dict__[name]) for name in argsNS.__dict__.keys()] )

        return argsDict
    

    
