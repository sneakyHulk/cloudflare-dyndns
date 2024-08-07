from CloudFlare import CloudFlare, exceptions
import waitress
from werkzeug.exceptions import HTTPException
from flask import Flask, send_from_directory, jsonify, request
import sys
import os

app = Flask(__name__)


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    print('Error: {}'.format(str(e)), file=sys.stderr)
    print('Route: {}'.format(request.full_path), file=sys.stderr)
    return jsonify(error=str(e)), code


@app.route('/', methods=['GET'])
def main():
    print('Main!', file=sys.stderr)
    token = request.args.get('token')
    zone = request.args.get('zone')
    record_name = request.args.get('record')
    ipv4 = request.args.get('ipv4')
    ipv6 = request.args.get('ipv6')
    cf = CloudFlare(token=token)

    if not token:
        print('Missing token URL parameter.', file=sys.stderr)
        return jsonify({'status': 'error', 'message': 'Missing token URL parameter.'}), 400
    if not zone:
        print('Missing zone URL parameter.', file=sys.stderr)
        return jsonify({'status': 'error', 'message': 'Missing zone URL parameter.'}), 400
    if not ipv4 and not ipv6:
        print('Missing ipv4 or ipv6 URL parameter.', file=sys.stderr)
        return jsonify({'status': 'error', 'message': 'Missing ipv4 or ipv6 URL parameter.'}), 400
    if not record_name:
    	print('No record name specified. Use zone name {} record'.format(zone), file=sys.stderr)
    	record_name = zone

    try:
        zones = cf.zones.get(params={'name': zone})

        if not zones:
            print('Zone {} does not exist.'.format(zone), file=sys.stderr)
            return jsonify({'status': 'error', 'message': 'Zone {} does not exist.'.format(zone)}), 404

        a_record = cf.zones.dns_records.get(zones[0]['id'], params={
            'name': '{}'.format(record_name), 'match': 'all', 'type': 'A'})
        aaaa_record = cf.zones.dns_records.get(zones[0]['id'], params={
            'name': '{}'.format(record_name), 'match': 'all', 'type': 'AAAA'})

        if ipv4 is not None and not a_record:
            print('A record for {} does not exist.'.format(record_name), file=sys.stderr)
            return jsonify({'status': 'error', 'message': 'A record for {} does not exist.'.format(zone)}), 404

        if ipv6 is not None and not aaaa_record:
            print('AAAA record for {} does not exist.'.format(record_name), file=sys.stderr)
            return jsonify({'status': 'error', 'message': 'AAAA record for {} does not exist.'.format(zone)}), 404

        if ipv4 is not None and a_record[0]['content'] != ipv4:
            print('name:', a_record[0]['name'], 'type: A', 'content:', ipv4, 'proxied:', a_record[0]['proxied'], 'ttl:',
                  a_record[0]['ttl'], file=sys.stderr)
            cf.zones.dns_records.put(zones[0]['id'], a_record[0]['id'], data={
                'name': a_record[0]['name'], 'type': 'A', 'content': ipv4, 'proxied': a_record[0]['proxied'],
                'ttl': a_record[0]['ttl']})

        if ipv6 is not None and aaaa_record[0]['content'] != ipv6:
            print('name:', aaaa_record[0]['name'], 'type: AAAA', 'content:', ipv6, 'proxied:',
                  aaaa_record[0]['proxied'], 'ttl:', aaaa_record[0]['ttl'], file=sys.stderr)
            cf.zones.dns_records.put(zones[0]['id'], aaaa_record[0]['id'], data={
                'name': aaaa_record[0]['name'], 'type': 'AAAA', 'content': ipv6, 'proxied': aaaa_record[0]['proxied'],
                'ttl': aaaa_record[0]['ttl']})
    except exceptions.CloudFlareAPIError as e:
        print(str(e), file=sys.stderr)
        return jsonify({'status': 'error', 'message': str(e)}), 500

    print('Update successful.', file=sys.stderr)
    return jsonify({'status': 'success', 'message': 'Update successful.'}), 200


@app.route('/healthz', methods=['GET'])
def healthz():
    print('Health check!', file=sys.stderr)
    return jsonify({'status': 'success', 'message': 'OK'}), 200


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    print('Favicon!', file=sys.stderr)
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


app.secret_key = os.urandom(24)
waitress.serve(app, host='0.0.0.0', port=80)
