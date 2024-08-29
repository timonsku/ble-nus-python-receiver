import sys
import asyncio
import argparse
import time
import struct

from bleak import BleakClient, BleakScanner
from bleak.uuids import uuid16_dict

class BLEUARTConnection:
    def __init__(self, client, rx, tx, pcm, rxPrint):
        self.client = client
        self.rx_char = rx
        self.tx_char = tx
        self.pcm = pcm
        self.rxPrint = rxPrint
        self.binary_file = None
        self.buffer = ''

    def __del__(self):
        self.binary_file.close()
       
    async def start(self):
        if self.pcm:
            self.binary_file = open('data.bin', 'wb')
        await self.client.start_notify(self.tx_char, self.rx_callback)
        print('Listening to notifications on the TX characteristic')

    def rx_callback(self, sender: int, data: bytearray):
        print("Received: "+str(len(data))+" bytes")
        if self.rxPrint:
            print(data)
        # write 16 bit data to binary file
        if self.pcm:
            for i in range(0, len(data), 2):
                self.binary_file.write(data[i:i+2])


    async def send(self, message):
        await self.client.write_gatt_char(self.rx_char, bytearray(message.encode('utf8')))


def get_uart_characteristics(client):
    # Find the Nordic UART service based on its description
    uart_service = None
    for service in client.services:  
        if service.description == 'Nordic UART Service':
            uart_service = service
            print('Found Nordic UART Service')
            break
    
    if uart_service is None:
        raise Exception('Failed to find UART service')

    rx = None
    tx = None
    for characteristic in uart_service.characteristics:
        print('Found characteristic:', characteristic.description)

        if characteristic.description == 'Nordic UART TX':
            tx = characteristic

        if characteristic.description == 'Nordic UART RX':
            rx = characteristic

        if rx is not None and tx is not None:
            break

    return (rx, tx)


async def rxtx(address_or_device, pcm, rxPrint):
    async with BleakClient(address_or_device) as client:
        while not client.is_connected:
            print('Waiting for connection to device')
            await asyncio.sleep(0.1)

        rx, tx = get_uart_characteristics(client)
        print('Found RX and TX characteristics:', rx, tx)

        uart_connection = BLEUARTConnection(client, rx, tx, pcm, rxPrint)
        await uart_connection.start()

        while True:
            await asyncio.sleep(1)


async def scan():
    devices = await BleakScanner.discover()

    for device in devices:
        print(f'{device.address}\t{device.name}')


async def discover_device_by_name(name):
    devices = await BleakScanner.discover()

    for device in devices:
        if device.name == name:
            return device

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send and receive Nordic BLE UART data')
    parser.add_argument('--address')
    parser.add_argument('--name')
    parser.add_argument('--pcm', default=False, action='store_true')
    parser.add_argument('--print', default=False, action='store_true')
    parser.add_argument('--scan', default=False, action='store_true')

    args = parser.parse_args()

    loop = asyncio.get_event_loop()

    if args.address and args.name:
        print('Specify either name or address but not both')
        sys.exit(1)

    if args.scan:
        asyncio.run(scan())
    else:
        if args.address:
            target = args.address
        elif args.name:
            device = loop.run_until_complete(discover_device_by_name(args.name))

            if device == None:
                print('Scan failed to find device with specified name')
                sys.exit(1)

            target = device

        loop.run_until_complete(rxtx(target, args.pcm, args.print))

