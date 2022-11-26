# import pickle

from flask import Flask, jsonify, request #, send_file, send_from_directory
from flask_csv import send_csv
from flask_cors import CORS
# import io

from filesfetcher import *
from updatechecker import *
from dispatcher import *
from decisiontable import *
from invertedindex import *

# import zipfile

print('[STATUS] - Instiating Flask app...')
app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False
# app.config["LABELS_FOLDER"] = "./labels/"
print('[STATUS] - ...done.')


dtab = DecisionTable(PARAMETERS)
dtab.build()


@app.route('/', methods=['GET'])
def home():

    return jsonify('This is the Decision Support System from Anderson A. Eduardo Lab.')


@app.route('/fetch/', methods=['GET'])
def fetch():

    print('[STATUS] - Instantiating FilesFetcher...')
    file_fetcher_system = FilesFetcher()
    print('[STATUS] - ...done.')

    print('[STATUS] - Fetching extant files...')
    output = file_fetcher_system.fetch_extant_files()
    print('[STATUS] - ...done.')
    
    print('[STATUS] Output:\n', output, '\n')

    keys = output[0].keys()

    return send_csv(
        output,
        "acr_guidelines_data.csv", 
        keys
    )


@app.route('/add/', methods=['GET'])
def add_email():

    print('[STATUS] - Instantiating Dispatcher...')
    dispatcher = Dispatcher()
    print('[STATUS] - ...done.')

    print('[STATUS] - Checking for e-mail consistency...')
    email = request.args.get('email', None)
    print('[STATUS] - ...done.')
    
    if email is not None and '@' in email:

        print('[STATUS] - Adding the new e-mail...')
        status = dispatcher.add_email(email)
        print('[STATUS] - ...done.')

        if status is True:

            print('[STATUS] Email added successfully.')

            return jsonify({ 
                'status': 200,
                'message': 'Email added successfully.'
            })

        else:

            print('[STATUS] This email already exists in the database.')

            return jsonify({ 
                'status': 204,
                'message': 'The provided email already exists in the database.'
            })

    else:

        print('WARNING: The provided email is inconsistent.')

        return jsonify({ 
            'status': 400,
            'message':'The provided email is inconsistent.'
        })


@app.route('/remove/', methods=['GET'])
def remove_email():

    print('[STATUS] - Instantiating Dispatcher...')
    dispatcher = Dispatcher()
    print('[STATUS] - ...done.')

    print('[STATUS] - Checking for e-mail consistency...')
    email = request.args.get('email', None)
    print('[STATUS] - ...done.')
    
    if email is not None and '@' in email:
    
        print('[STATUS] - Removing e-mail...')
        status = dispatcher.remove_email(email)
        print('[STATUS] - ...done.')

        if status is True:

            print('[STATUS] - E-mail removed.')

            return jsonify({
            'status': 200,
            'message':'Email removed.'
            })

        else:

            print('[STATUS] - The provided email was not found in the database.')

            return jsonify({
                'status': 400,
                'message':'The provided email was not found in the database.'
            })


    else:

        print('WARNING: The provided email is inconsistent.')

        return jsonify({ 
            'status': 400,
            'message':'The provided email is inconsistent.'
        })


@app.route('/query/', methods=['GET'])
def query():

    age = request.args.get('age', None, type=str)
    sex = request.args.get('sex', None, type=str)
    clinical_indication = request.args.get('clinicalindication', '', type=str)
    subcategory = request.args.get('subcategory', '', type=str)
    top_n = request.args.get('top_n', 1, type=int)

    user_query = {
        'IDADE': age,
        'SEXO': sex,
        'INDICAÇÃO CLÍNICA': clinical_indication,
        'SUBCATEGORIA': subcategory,
    }

    print('user_query:', user_query)

    output = dtab.query(user_query, top_n = int(top_n))

    return jsonify(output)


@app.route('/autocomplete_category/', methods=['GET'])
def autocomplete_category():

    atcp = Autocomplete()

    output = atcp.get_clinical_condition()

    return jsonify(output)


@app.route('/autocomplete_subcategory/', methods=['GET'])
def autocomplete_subcategory():

    atcp = Autocomplete()

    output = atcp.get_subcategory()

    return jsonify(output)
    

@app.route('/autocomplete_sex/', methods=['GET'])
def autocomplete_sex():

    atcp = Autocomplete()

    output = atcp.get_sex()

    return jsonify(output)


@app.route('/autocomplete_age/', methods=['GET'])
def autocomplete_age():

    atcp = Autocomplete()

    output = atcp.get_age()

    return jsonify(output)


if __name__ == '__main__':

    app.run(host="0.0.0.0", debug=False)
