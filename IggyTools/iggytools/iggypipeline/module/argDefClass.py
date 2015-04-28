import re
from pprint import pformat
from textwrap import TextWrapper

firstColStart = 4   
secondColStart = 35
secondColWidth = 70
wrapper = TextWrapper(initial_indent = '', subsequent_indent = '', width = secondColWidth)

class ArgDef(object):
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
        if 'default' in kwargs:
            self.default = kwargs['default']
        else:
            self.default = None

        name = [re.sub('--','',x) for x in self.args if re.match('--|\w',x)][0]  #define self.name via command-line arg name
        self.name = re.sub('-','_',name)  

        self.value = self.default


    def add(self, parser):
        parser.add_argument(*self.args, **self.kwargs)


    def show(self):  #print arg properties in specific order

        indent = firstColStart * ' '
        firstColWidth = secondColStart - firstColStart

        if 'help' in self.kwargs:  #print arg name and help message if it exists

            text = self.kwargs['help']
            #suppress default substring for command-line interface
            match = re.search('[dD]efault:', text)
            if match:
                text = text[:match.start()]
            lines = wrapper.wrap(text)
            print '%s%s%s' % (indent, self.name.ljust(firstColWidth), lines.pop(0))
            for line in lines:
                print '%s%s' % (indent.rjust(secondColStart), line)
        else:
            print '%s%s' % (indent, self.name)  #print arg name
        
        for prop in ['default', 'nargs']:
            if prop in self.kwargs:
                print '%s%s: %s' % (indent.rjust(secondColStart), prop, pformat(self.kwargs[prop]))

        if 'type' in self.kwargs:
            t = self.kwargs['type']
            line = 'type: '
            if t == str:
                line += 'str'
            elif t == int:
                line += 'int'
            elif t == list:
                line += 'list'
            elif t == bool:
                line += 'bool'
            else:
                line += 'unkown'
            print '%s%s' % (indent.rjust(secondColStart), line)

    def __repr__(self):
        return '\n'.join(['%s:  %s' % (name, value) for name,value in self.kwargs.iteritems()])
