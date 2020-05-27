# receptor Reiable UDP
from random import random

from helper import *
from argparse import ArgumentParser
import socket
import logging

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

def main():
    parser = ArgumentParser(usage=__file__ + ' '
                                             '-p/--port PORT'
                                             '-f/--fisier FILE_PATH',
                            description='Reliable UDP Receptor')

    parser.add_argument('-p', '--port',
                        dest='port',
                        default='10000',
                        help='Portul pe care sa porneasca receptorul pentru a primi mesaje')

    parser.add_argument('-f', '--fisier',
                        dest='fisier',
                        help='Calea catre fisierul in care se vor scrie octetii primiti')

    # Parse arguments
    args = vars(parser.parse_args())
    port = int(args['port'])
    fisier = args['fisier']
    f = open(fisier, 'w')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

    adresa = '0.0.0.0'
    server_address = (adresa, port)
    sock.bind(server_address)
    logging.info("Serverul a pornit pe %s si portnul portul %d", adresa, port)

    while True:
        logging.info('Asteptam mesaje...')
        data, address = sock.recvfrom(MAX_SEGMENT)
        print("da")
        header = data[:8]
        mesaj = data[8:]
        seq_nr, checksum, flags = parse_header_emitator(header)
        ack_nr = 0
        if flags == 'S' or flags == 'F':
            ack_nr = seq_nr + 1
        elif flags == 'P':
            ack_nr = seq_nr

        f.write(mesaj)

        if not verifica_checksum(checksum):
            checksum = 0
            window = random.randint(1, 5)
            octeti = create_header_receptor(ack_nr=ack_nr,
                                            checksum=checksum,
                                            window=window)
            sock.sendto(address, octeti)
        else:
            checksum = 0
            window = 0
            octeti = create_header_receptor(ack_nr=ack_nr,
                                            checksum=checksum,
                                            window=window)
            sock.sendto(address, octeti)

        '''
        TODO: pentru fiecare mesaj primit
        1. verificam checksum
        2. parsam headerul de la emitator
        3. trimitem confirmari cu ack = seq_nr+1 daca mesajul e de tip S sau F
                               cu ack = seq_nr daca mesajul e de tip P
        4. scriem intr-un fisier octetii primiti
        5. verificam la sfarsit ca fisierul este la fel cu cel trimis de emitator
        '''


if __name__ == '__main__':
    main()
