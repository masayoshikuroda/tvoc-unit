#!/usr/bin/env python3
# coding=utf-8
import sys
import struct
from datetime import datetime
from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_DGRAM
from socket import SOL_SOCKET, SO_BROADCAST
import asyncio
from bleak import BleakClient

GATT_CHARACTERISTIC_UUID_TVOC = '00005011-0000-1000-8000-00805f9b34fb'
GATT_CHARACTERISTIC_UUID_ECO2 = '00005012-0000-1000-8000-00805f9b34fb'

argparser =  ArgumentParser(description='Connect BTWATTCH2 via bluetooth and broadcast measured values via UDP.')
argparser.add_argument('-d', '--dest', type=str,   dest='dest', default='255.255.255.255', help='destination mac address to broadcast')
argparser.add_argument('-p', '--port', type=int,   dest='port', default=7000,              help='destination port number to broadcast')
argparser.add_argument('-s', '--sec',  type=float, dest='sec',  default=1.0,               help='measurement interval') 
argparser.add_argument('-v', '--verbose',          dest='verbose', action='store_true',    help='dump result to stdout')
argparser.add_argument('id',           type=str,                                           help='device mac addres to connect')
args = argparser.parse_args()

id = args.id
dest = args.dest
port = args.port
sec = args.sec
verbose = args.verbose

s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

def on_value(tvoc, eco2):
    dt = datetime.now().strftime('%Y–%m–%d %H:%M:%S')
    if verbose:
        print("{0} {1:1d}[ppb] {2:1d}[ppm]".format(dt, tvoc, eco2))
    msg = '{"tvoc":' + str(tvoc) + ',"eco2":' + str(eco2) + '}'
    s.sendto(msg.encode(), (dest, port))   
 
async def run(loop):
    client = BleakClient(id)
    await client.connect()
    print("connected!")

    while True:
        tvoc = struct.unpack('H', await client.read_gatt_char(GATT_CHARACTERISTIC_UUID_TVOC))[0]
        eco2 = struct.unpack('H', await client.read_gatt_char(GATT_CHARACTERISTIC_UUID_ECO2))[0]
        on_value(tvoc, eco2)
        await asyncio.sleep(sec, loop=loop)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
