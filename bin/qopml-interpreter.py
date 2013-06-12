'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from qopml.interpreter.model.parser import ParserException
from qopml.interpreter.simulator import EnvironmentDefinitionException
from qopml.interpreter.simulator.state import PrintExecutor
from qopml.interpreter.app import Interpreter, Builder
from qopml.interpreter.simulator.error import RuntimeException
from qopml.interpreter.module import timeanalysis

debug = False

def main(qopml_model):

    ############### DEBUG ###############    
    if debug:
        builder = Builder()
        store = builder.build_store()
        parser = builder.build_parser(store, [])
        parser.lexer.input(qopml_model)
        while True:
            print  parser.lexer.current_state()
            tok = parser.lexer.token()
            if not tok:
                break
            print tok
            print ""
        print 'Errors: ' + str(parser.get_syntax_errors())
        print ""
        print ""
    
    #####################################
    interpreter = Interpreter(builder=Builder())
    try:
        interpreter.set_qopml_model(qopml_model)
        interpreter.register_qopml_module(timeanalysis.Module())
        interpreter.prepare()
        
        for thread in interpreter.threads: 
            thread.simulator.get_executor().prepend_instruction_executor(PrintExecutor(sys.stdout))
            
        interpreter.run()
    except EnvironmentDefinitionException, e:
        print "Error on creating environment: %s" % e
        if len(e.errors) > 0:
            print "Errors:"
            sys.stderr.write('\n'.join(e.errors))
            print
        return
    except ParserException, e:
        print "Parsing error: %s" % e
        if len(e.syntax_errors):
            print "Syntax errors:"
            sys.stderr.write('\n'.join(e.syntax_errors))
            print
        return
    except RuntimeException, e:
        print "Runtime error: %s" % e
        return
    #####################################
    
if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print "Usage: python qopml-interpreter.py qopml-model-file"
        sys.exit(1)
    
    if not os.path.exists(sys.argv[1]):
        print "File '%s' does not exist" % sys.argv[1]
        sys.exit(2)
    
    f = open(sys.argv[1], 'r')
    qopml_model = f.read()
    f.close()
    
    main(qopml_model)