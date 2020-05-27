# emitator Reliable UDP
import traceback

from helper import *
from argparse import ArgumentParser
import socket
import logging
import sys
import random

seq_nr = 0

logging.basicConfig(format=u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level=logging.NOTSET)


def connect(sock, adresa_receptor):
    '''
    Functie care initializeaza conexiunea cu receptorul.
    Returneaza ack_nr de la receptor si window
    '''
    MAX_UINT32 = 0xFFFFFFFF
    seq_nr = 0  # TODO: setati initial sequence number
    flags = 'S'
    checksum = 0
    octeti_header_fara_checksum = create_header_emitator(seq_nr=seq_nr, flags=flags, checksum=checksum)
    mesaj = octeti_header_fara_checksum
    checksum = calculeaza_checksum(mesaj)
    octeti_header_cu_checksum = create_header_emitator(seq_nr=seq_nr, flags=flags, checksum=checksum)

    mesaj = octeti_header_cu_checksum

    sock.sendto(mesaj, adresa_receptor)

    done = False
    while not done:
        try:
            print("hello")
            data, server = sock.recvfrom(MAX_SEGMENT)
            done = True
        except socket.timeout as e:
            logging.info("Timeout la connect, retrying...")
            done = False

    print("hello2")
    if verifica_checksum(data) is False:
        # daca checksum nu e ok, mesajul de la receptor trebuie ignorat
        return -1, -1

    ack_nr, checksum, window = parse_header_receptor(data)

    logging.info('Ack Nr: "%d"', ack_nr)
    logging.info('Checksum: "%d"', checksum)
    logging.info('Window: "%d"', window)

    return ack_nr, window


def finalize(sock, adresa_receptor, seq_nr):
    '''
    Functie care trimite mesajul de finalizare
    cu seq_nr dat ca parametru.
    '''
    # TODO:
    # folositi pasii de la connect() pentru a construi headerul
    # valorile de checksum si pentru a verifica primirea mesajului a avut loc

    flags = 'F'
    checksum = 0
    octeti_header_fara_checksum = create_header_emitator(seq_nr, flags, checksum)

    mesaj = octeti_header_fara_checksum
    checksum = calculeaza_checksum(mesaj)
    octeti_header_cu_checksum = create_header_emitator(seq_nr, flags, checksum)

    mesaj = octeti_header_cu_checksum

    sock.sendto(mesaj, adresa_receptor)

    done = False
    while not done:
        try:
            data, server = sock.recvfrom(MAX_SEGMENT)
            done = True
        except socket.timeout as e:
            logging.info("Timeout la connect, retrying...")
            done = False
    if verifica_checksum(data) is False:
        # daca checksum nu e ok, mesajul de la receptor trebuie ignorat
        return -1, -1

    ack_nr, checksum, window = parse_header_receptor(data)

    logging.info('Ack Nr: "%d"', ack_nr)
    logging.info('Checksum: "%d"', checksum)
    logging.info('Window: "%d"', window)

    return 0


def send(sock, adresa_receptor, seq_nr, window, octeti_payload):
    '''
    Functie care trimite octeti ca payload catre receptor
    cu seq_nr dat ca parametru.
    Returneaza ack_nr si window curent primit de la server.
    '''
    # TODO...
    sock.bind(adresa_receptor)
    flags = 'P'
    checksum = 0
    seq_nr = seq_nr + len(octeti_payload)
    octeti_header_fara_checksum = create_header_emitator(seq_nr=seq_nr, flags=flags, checksum=checksum)
    mesaj = octeti_header_fara_checksum + octeti_payload
    checksum = calculeaza_checksum(mesaj)
    octeti_header_cu_checksum = create_header_emitator(seq_nr=seq_nr, flags=flags, checksum=checksum)
    mesaj = octeti_header_cu_checksum + octeti_payload

    sock.sendto(mesaj, adresa_receptor)

    done = False
    while done == False:
        try:
            data, server = sock.recvfrom(MAX_SEGMENT)
            done = True
        except socket.timeout as e:
            logging.info("Timeout la connect, retrying...")

    if verifica_checksum(data) is False:
        # daca checksum nu e ok, mesajul de la receptor trebuie ignorat
        return -1, -1

    ack_nr, checksum, window = parse_header_receptor(data)

    logging.info('Ack Nr: "%d"', ack_nr)
    logging.info('Checksum: "%d"', checksum)
    logging.info('Window: "%d"', window)

    return ack_nr, window


def main():
    parser = ArgumentParser(usage=__file__ + ' '
                                             '-a/--adresa IP '
                                             '-p/--port PORT'
                                             '-f/--fisier FILE_PATH',
                            description='Reliable UDP Emitter')

    parser.add_argument('-a', '--adresa',
                        dest='adresa',
                        default='receptor',
                        help='Adresa IP a receptorului (IP-ul containerului, localhost sau altceva)')

    parser.add_argument('-p', '--port',
                        dest='port',
                        default='10000',
                        help='Portul pe care asculta receptorul pentru mesaje')

    parser.add_argument('-f', '--fisier',
                        dest='fisier',
                        help='Calea catre fisierul care urmeaza a fi trimis')

    # Parse arguments
    args = vars(parser.parse_args())

    ip_receptor = args['adresa']
    port_receptor = int(args['port'])
    fisier = args['fisier']
    print(100 * '*' + 'Fisierul este')
    print(fisier)
    adresa_receptor = (ip_receptor, port_receptor)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    # setam timeout pe socket in cazul in care recvfrom nu primeste nimic in 3 secunde
    sock.bind(adresa_receptor)
    sock.settimeout(3)
    try:
        ack_nr, window = connect(sock, adresa_receptor)
        file_descriptor = open(fisier, 'rb')
        for i in range(window):
            segment = citeste_segment(fisier)
            ack_nr, window = send(sock, adresa_receptor, seq_nr, window, segment)
        ## TODO: send trebuie sa trimită o fereastră de window segmente
        # până primșete confirmarea primirii tuturor segmentelor
        ##

        finalize(sock, adresa_receptor, seq_nr)
        file_descriptor.close()
    except Exception as e:
        logging.exception(traceback.format_exc())
        sock.close()


if __name__ == '__main__':
    main()