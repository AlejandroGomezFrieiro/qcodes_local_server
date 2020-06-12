##### This file creates a remote Pyro4 server based on the old qtlab version, but adapted to modern Python 3
import Pyro4
import sys
import socket
import threading

Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED = ['json','marshal','serpent', 'pickle']
@Pyro4.expose
class Server():
    def __init__(self):
        print('Starting Pyro4 server')
        self.instruments = dict()
    @staticmethod
    def create_instrument(instrument_class, *args, **kwargs):
        '''
        Returns and instance of a class of type instrument_class from a name and an ip address, passing **kwargs'''
        return instrument_class(*args, **kwargs)

    def close(self):
        print('Stopping Pyro4 Server')

    def __del__(self):
        self.close()

def main():
    local_IP = socket.gethostbyname(socket.getfqdn())
    print("Default IP is "+local_IP)
    ############IF IT DOES NOT RUN BY DEFAULT, COMPLETE THIS STRING WITH THE LAB IP OF THE SYSTEM
    #local_IP = '192.168.1.'


    if local_IP.startswith('10.184.25.'):
        daemon = Pyro4.Daemon(host=local_IP) # Rack 3
    else:
        print('Default IP method does not work. \n')
        print('Please check the server.py file local_IP variable and add the proper IP')
        sys.exit('Exiting...')

    # Create the daemon's uri
    uri = daemon.register(Server)

    # Write the daemon's uri into the drive.
    # with open(r'Z:/SMP/Research/EQUS-SQDLab/DataAnalysis/Notebooks/qcodes/FPGA_Rack3_URI.txt' , 'w') as fh:
    #     fh.write(str(uri))
    print(uri)

    print('Starting loop')
    daemon.requestLoop()

if __name__=="__main__":
    main()

# Create a daemon to be accessed, in this IP