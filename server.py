##### This file creates a remote Pyro4 server based on the old qtlab version, but adapted to modern Python 3
import Pyro4
import sys
import socket
import threading
import qcodes as qc
import inspect
from collections import defaultdict


Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED = ['json','marshal','serpent', 'pickle']

from qcodes import Instrument

## Add all the instrument you want to use to the station in the same way the DummyInstrument is added

from qcodes.tests.instrument_mocks import DummyInstrument

test_instrument = DummyInstrument('test_name')

station = qc.Station()
station.add_component(test_instrument)

@Pyro4.expose
class QcodesRemoteServer(object):
    def __init__(self):
        print('Starting Pyro4 server')
        self.locks = defaultdict(lambda: threading.Lock())

    
    def ins_get(self, instrument_name: str, parameter: str):
        '''Get the value of a parameter inside the instrument'''
        with self.locks['instrument']:
            value = station.components[instrument_name].get(parameter)
        return value

    def ins_set(self, instrument_name: str, parameter: str, args):
        '''set the value of parameter of instrument ins'''
        with self.locks['instrument']:
            return station.components[instrument_name].set(parameter, *args)

    def ins_call(self, instrument_name: str, function, args, kwargs):
        '''call function of instrument ins with *args and **kwargs'''
        func = getattr(station.components[instrument_name], function)
        with self.locks['ins']:
            result = func(*args, **kwargs)
        if isinstance(result, np.ndarray):
            result = pickle.dumps(result)
        return result

    def get_instrument_names(self):
        '''get the names of all known instruments'''
        tmp = []
        for component in station.components:
            tmp.append(component)
        return tmp

    def get_function_names(self, instrument_name: str):
        '''get names of the functions registered in instrument ins'''
        tmp_instrument = station.components[instrument_name]
        return tmp_instrument.functions

    def get_parameters(self, instrument_name: str):
        '''get names of the functions registered in instrument ins'''
        tmp_instrument = station.components[instrument_name]
        tmp = []
        for parameter in tmp_instrument.parameters:
            tmp.append(parameter)
        return tmp

    def get_function_spec(self, instrument_name, function):
        '''get calling convention and documentation of function of instrument ins'''
        if function not in self.get_function_names(instrument_name):
            return None
        func = getattr(station.components[instrument_name], function)
        argspec = inspect.getargspec(func)
        return dict(argspec=dict(args=argspec.args,
                                 varargs=argspec.varargs,
                                 keywords=argspec.keywords,
                                 defaults=argspec.defaults, 
                                 ndefaults=0 if argspec.defaults is None else 
                                           len(argspec.defaults)),
                    calldoc=inspect.formatargspec(*argspec), 
                    doc=getattr(func, '__doc__'))

    def close(self):
        print('Stopping Pyro4 Server')

    def __del__(self):
        self.close()

def main():
    ########COMPLETE THIS STRING WITH THE LAB IP OF THE COMPUTER YOU ARE CREATING THE SERVER IN
    local_IP = '192.168.1.xxx'
    print("Default IP is "+local_IP)

    daemon = Pyro4.Daemon(host=local_IP)



    # if local_IP.startswith('192.168.1.'):
    #     daemon = Pyro4.Daemon(host=local_IP) # Rack 3
    # else:
    #     print('Default IP method does not work. \n')
    #     print('Please check the server.py file local_IP variable and add the proper IP')
    #     sys.exit('Exiting...')

    # Create the daemon's uri
    uri = daemon.register(Server)

    # Write the daemon's uri into the drive.
    with open(r'path_to_drive/DataAnalysis/Notebooks/qcodes/Server_uri.txt' , 'w') as fh:
        fh.write(str(uri))
    print(uri)

    daemon.requestLoop()

if __name__=="__main__":
    main()

# Create a daemon to be accessed, in this IP