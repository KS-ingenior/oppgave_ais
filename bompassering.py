# -*- coding: utf-8 -*-

import random
import datetime
from zipfile import ZipFile

# Create some words to choose from
words = {
    'bomstasjon': [
        'E18 Lysaker (32VNM9087342403)',
        'Bærumsveien (32VNM9080144357)',
        'Griniveien (32VNM9126147264)',
        'E18 Lysaker (32VNM9087342403)',
        'E18 Lysaker (32VNM9087342403)',
        'E18 Lysaker (32VNM9087342403)',
        'E18 Lysaker (32VNM9087342403)',
    ],
    'number': [i+1 for i in range(10023, 99899,167)],
    'kjennetegn': [
        'AA',
        'AB',
        'AC',
        'BL',
        'BP',
        'BV',
        'CB',
        'CP',
        'CT',
        'FW',
        'HR',
        'SU',
        'HX',
        'DA',
        'DY',
        'DP',
        'DT',
        'DY',
        'DZ',
        'DL',
        'NK',
        'AP',
    ],
    'farge': [
        'Grå',
        'Blå',
        'Hvit',
        'Sølv',
        'Svart',
        'Hvit',
        'Oransj',
        'Gul',
        'Rød',
        'Grønn',
    ],
    'biltype': [
        'VW Passat'.upper(),
        'VW Caravelle'.upper(),
        'VW Transporter'.upper(),
        'Skoda Superb'.upper(),
        'Toyota RAV4'.upper(),
        'Volvo XC40'.upper(),
        'VW Golf'.upper(),
        'Ford Ranger'.upper(),
        'BMW X3'.upper(),
        'Kia Niro'.upper(),
        'Hyundai Kona'.upper(),
        'Mercedes EQC'.upper(),
        'MG ZS EV'.upper(),
        'Polestar 2'.upper(),
        'Tesla Model Y'.upper(),
        'Tesla Model 3'.upper(),
        'Audi e-tron'.upper(),
        'Peugeot 2008'.upper(),
        'Volvo XC60'.upper(),
    ],
    'dir1': [
        'vest',
        'øst',
        ]
}


# Message template with placeholders
msg = """DTG {dtg}
BOMSTASJON: {bomstasjon}

{farge} {biltype} med registreringsnummer {kjennetegn}{number} har passert bomstasjon {bomstasjon} i retning {dir1} DTG {dtg}.

"""

def dt2dtg(dt):
    # DTG 271913Anov08
    return dt.strftime('%d%H%MZ%b%y').upper()

def bompassering(bbox, dt_from=None, dt_length=None):
  
    # Message data
    msg_data = {}

    if dt_from is None:
        dt_from = datetime.datetime.now(tz=datetime.timezone.utc)

    if dt_length is None:
        dt_length = datetime.timedelta(hours=1)

    # Calculate random datetimes for message
    dt_length_seconds = int(dt_length.total_seconds())
    dt_sec = random.randint(0,dt_length_seconds)
    dt_msg_sec = random.randint(dt_sec, dt_length_seconds)

    # Convert to datetime
    msg_data['dtg'] = dt2dtg(dt_from + datetime.timedelta(seconds=dt_sec))
    msg_data['dtg_msg'] = dt2dtg(dt_from + datetime.timedelta(seconds=dt_msg_sec))

    # Chose random data
    for w in words.keys():
        msg_data[w] = random.choice(words[w])

    # Generate message
    gen_msg = msg.format(**msg_data)

    # Create a filename
    fname = '{dtg}_{kjennetegn}{number}.txt'.format(**msg_data).upper()

    return gen_msg, fname

def create_bompassering(bbox, outfile, n=1253):

    with ZipFile(outfile, 'w') as myzip:
        
        for i in range(n):
            gen_msg, fname = bompassering(bbox)

            with myzip.open(fname, mode='w') as myfile:
                myfile.write(gen_msg.encode('utf-8'))

if __name__ == '__main__':

    bbox = dict(top=61, bottom=60, right=9, left=8)

    outfile = 'bompassering.zip'
    
    create_bompassering(bbox, outfile, n=1253)
