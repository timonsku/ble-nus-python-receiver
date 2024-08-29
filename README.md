## Install dependencies

Python 3 needs to be installed. Whatever version is compatible with the latest version of bleak.

```
pip install -r requirements.txt
```

## Usage

To list available devices you can run a scan

```
python ble_data_bridge/__init__.py --scan
```

To connect to a device
```
python ble_data_bridge/__init__.py --name "device name"
```

To save incoming data as a 16bit PCM binary stream:
```
python ble_data_bridge/__init__.py --name "device name" --pcm
```

To print the incoming data to console:
```
python ble_data_bridge/__init__.py --name "device name" --print
```

No write functionality exposed via CLI, need to add that to the script if needed.

Credits:
Based on https://github.com/jmpinit/python_ble_uart_example