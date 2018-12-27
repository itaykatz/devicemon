import click
from flask import Flask, jsonify, request
from src.scanner import TsharkScanner

app = Flask('devicemon')


@app.route('/devices', methods=['GET'])
def get_devices():
    scan_time = request.args.get('scan_time', 1)
    app.logger.info('Entering scanner...')
    scanner = app.config.get('scanner')

    result = scanner.scan(scan_time=int(scan_time))
    return jsonify(result)


@app.route('/test_devices')
def get_test_devices():
    scanner = app.config.get('scanner')
    scan_time = request.args.get('scan_time', 1)

    result = scanner.scan(in_file='test/tshark-temp', scan_time=int(scan_time))
    return jsonify(result)


@click.command()
@click.option('-i', '--interface', help='interface to use', default='wlan1mon')
@click.option('-p', '--tmp_path',  help='temp path for tshark scan results', default='/tmp/tshark-temp')
def main(interface, tmp_path):
    app.config['scanner'] = TsharkScanner(interface=interface, tmp_path=tmp_path)
    app.run(debug=True, port=80, host='0.0.0.0')


if __name__ == '__main__':
    main()




