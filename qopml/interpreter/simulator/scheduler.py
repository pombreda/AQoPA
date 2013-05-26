'''
Created on 15-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from qopml.interpreter.simulator.state import InstructionsContext,\
    InstructionsList
from qopml.interpreter.model import HostProcess

class Scheduler():
    
    def __init__(self, host):
        raise NotImplementedError()
    
    def finished(self):
        """
        Returns True if host is finished.
        """
        raise NotImplementedError()
    
    def get_current_context(self):
        """
        Returns instructions context executed in current state.
        """
        raise NotImplementedError()
    
    def goto_next_instruction_context(self):
        """
        Move hosts state to next instructions list.
        """
        raise NotImplementedError()

class FifoScheduler(Scheduler):
    
    def __init__(self, host):
        """ """
        self.host = host
        self.context = self._build_context()
    
    def _build_context(self):
        """ """
        context = InstructionsContext()
        context.add_instructions_list(self.host.instructions_list)
        return context
    
    def finished(self):
        """ """
        return self.context.finished()
    
    def get_current_context(self):
        """ """
        return self.context
    
    def goto_next_instruction_context(self):
        """ """
        # Fifo has only one context
        pass
        

class RoundRobinScheduler(Scheduler):
    
    def __init__(self, host):
        """ """
        self.host = host
        self.contexts = []
        self._current_context_index = 0
    
    def _build_contexts(self):
        """ """
        host_instructions_context = InstructionsContext()
        host_instructions_list = []
        
        host_context_added = False
        for i in self.host.instructions_list:
            
            if isinstance(i, HostProcess):
                process = i
                
                if len(process.instructions_list) > 0:
                    process_context = InstructionsContext()
                    self.contexts.append(process_context)
                    
                    process_context.add_instructions_list(
                                        process_context.instructions_list, 
                                        process)
            else:
                host_instructions_list.append(i)
                if not host_context_added:
                    self.contexts.append(host_instructions_context)
                    host_context_added = True
                    
        if len(host_instructions_list) > 0:
            host_instructions_context.add_instructions_list(InstructionsList(host_instructions_list))
            
    def finished(self):
        """ """
        for c in self.contexts:
            if not c.finished():
                return False
        return True
    
    def get_current_context(self):
        """ """
        return self.contexts[self._current_context_index]
    
    def goto_next_instruction_context(self):
        """ """
        now_index = self._current_context_index
        
        self._current_context_index = (self._current_context_index + 1) % len(self.contexts)
        
        while now_index != self._current_context_index and self.get_current_context().finished():
            self._current_context_index = (self._current_context_index + 1) % len(self.contexts)
        
        
SCHEDULE_ALGORITHM_ROUND_ROBIN  = 'rr'
SCHEDULE_ALGORITHM_FIFO         = 'fifo'

def create(algorithm):
    if algorithm == SCHEDULE_ALGORITHM_FIFO:
        return FifoScheduler()
    elif  algorithm == SCHEDULE_ALGORITHM_ROUND_ROBIN:
        return RoundRobinScheduler()
    