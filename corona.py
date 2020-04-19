import flask
from flask import request, jsonify
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
import matplotlib as mpl 
from urllib.request import urlopen
import json
import csv
import json


app = flask.Flask(__name__)
app.config["DEBUG"] = True


url = "https://api.rootnet.in/covid19-in/unofficial/covid19india.org/statewise/history"
url_data = json.loads(urlopen(url).read().decode("utf-8"))

# Create some test data for our catalog in the form of a list of dictionaries.
covid19 = {"success":True,
        "existing":
        {
            "description" : "Statewise_History",
            "url" : "https://api.rootnet.in/covid19-in/unofficial/covid19india.org/statewise/history"
        },
        "developed":
           
        {
            "Dataset":"Max 5 States",
            "data":""
        }
    }

@app.route('/data/')
def example():
    global covid19
    history_load = url_data['data']['history']
    f = open('datewise_data.csv', 'w', newline='')
    csv_file = csv.writer(f)
    csv_file.writerow(["Date", "State", "Confirmed", "Recovered", "Deaths"]) #",Active"
    for history in history_load:
        for statewise_data in history['statewise']:
            csv_file.writerow([history['day'],
                statewise_data['state'],
                statewise_data['confirmed'],
                statewise_data['recovered'],
                statewise_data['deaths']]) #, statewise_data['active']
    f.close()
    # Section 2 - Loading , and Selecting Data
    df1 = pd.read_csv('datewise_data.csv', parse_dates=['Date'])
    df=df1.drop_duplicates()

    # Section 3 - Creating a Summary Column
    date = df['Date'].unique()
    date.sort()
    df2 = df[['Date', 'State', 'Confirmed']].copy()
    df2=df2.loc[df2['Date'] == date[-1]]
    df2=df2[['State', 'Confirmed']].copy()
    df3 = df[['Date', 'State', 'Confirmed']].copy()
    df3=df3.loc[df3['Date'] == date[-2]]
    df3=df3[['State', 'Confirmed']].copy()
    #print(df3)
    df_inner = pd.merge(df2, df3, on='State', how='inner')
    df_inner['diff']=df_inner['Confirmed_x'] - df_inner['Confirmed_y']
    # print(df_inner)

    df=df_inner.nlargest(5,'diff')
    if covid19['developed']['Dataset'].lower() == "max 5 states":
        covid19['developed']['data'] = json.loads(df.to_json(orient="records"))
    return jsonify(covid19)

@app.route('/nsd/<string:data>',methods=['GET'])
def nsd(data):
    print(type(data),data)
    return data

@app.route('/api/v1/resources/covid19/neighbouringdata/<string:sid>',methods=['GET'])
def neighbouringdata(sid):
    history_load = url_data['data']['history']
    f = open('datewise_data_nsd.csv', 'w', newline='')
    csv_file = csv.writer(f)
    csv_file.writerow(["Date", "State", "Confirmed", "Recovered", "Deaths"])
    for history in history_load:
        for statewise_data in history['statewise']:
            csv_file.writerow([history['day'],
                           statewise_data['state'],
                           statewise_data['confirmed'],
                           statewise_data['recovered'],
                           statewise_data['deaths']]) #, statewise_data['active']
    f.close()


    # Section 2 - Loading , and Selecting Data
    df = pd.read_csv('datewise_data_nsd.csv', parse_dates=['Date'])

    # Section 2.1 - Creating Datafaram for All State Neighboring States
    data = {'Maharashtra': pd.Series(['Gujarat', 'Telangana', 'Maharashtra', 'Delhi', 'Madhya Pradesh','Karnataka','Goa','Chhattisgarh']),
            'Tamil Nadu' : pd.Series(['Tamil Nadu','Puducherry','Kerala','Andhra Pradesh','Karnataka','Delhi']),
            'Delhi' : pd.Series(['Delhi','Uttar Pradesh','Haryana']),
            'Telangana' : pd.Series(['Telangana','Maharashtra','Karnataka','Chhattisgarh','Delhi','Andhra Pradesh']),
            'Rajasthan' : pd.Series(['Rajasthan','Gujarat','Madhya Pradesh','Punjab','Uttar Pradesh','Haryana','Delhi']),
            'Kerala' : pd.Series(['Kerala','Tamil Nadu','Karnataka','Puducherry','Delhi']),
            'Uttar Pradesh' : pd.Series(['Uttar Pradesh','Madhya Pradesh','Rajasthan','Delhi','Haryana','Uttarakhand','Bihar','Chhattisgarh','Jharkhand']),
            'Andhra Pradesh' :pd.Series(['Andhra Pradesh','Delhi','Chhattisgarh','Tamil Nadu','Karnataka','Odisha','Puducherry']),
            'Madhya Pradesh' :pd.Series(['Madhya Pradesh','Gujarat','Rajasthan','Maharashtra','Chhattisgarh','Uttar Pradesh','Delhi']),
            'Karnataka' :pd.Series(['Karnataka','Maharashtra','Tamil Nadu','Goa','Kerala','Andhra Pradesh','Telangana','Delhi']),
            'Gujarat' :pd.Series(['Gujarat','Rajasthan','Madhya Pradesh','Maharashtra','Delhi','Dadra and Nagar Haveli','Daman and Diu']),
            'Haryana' :pd.Series(['Haryana','Punjab','Himachal Pradesh','Rajasthan','Delhi','Uttarakhand','Uttar Pradesh','Chandigarh']),
            'Jammu and Kashmir' :pd.Series(['Jammu and Kashmir','Punjab','Himachal Pradesh','Delhi','Ladakh']),
            'Punjab' :pd.Series(['Punjab','Jammu and Kashmir','Haryana','Himachal Pradesh','Rajasthan','Delhi','Chandigarh']),
            'West Bengal' :pd.Series(['West Bengal','Odisha','Bihar','Jharkhand','Assam','Sikkim','Delhi']),
            'Odisha' :pd.Series(['Odisha','West Bengal','Chhattisgarh','Jharkhand','Chhattisgarh','Andhra Pradesh','Delhi']),
            'Bihar' :pd.Series(['Bihar','Uttar Pradesh','Jharkhand','West Bengal','Delhi']),
            'Uttarakhand' :pd.Series(['Uttarakhand','Haryana','Uttar Pradesh','Himachal Pradesh','Delhi']),
            'Assam' :pd.Series(['Assam','West Bengal','Manipur','Mizoram','Arunachal Pradesh','Nagaland','Meghalaya','Tripura','Delhi']),
            'Chandigarh' :pd.Series(['Chandigarh','Punjab','Haryana','Delhi']),
            'Himachal Pradesh' :pd.Series(['Himachal Pradesh','Punjab','Haryana','Uttarakhand','Uttarakhand','Jammu and Kashmir','Ladakh','Delhi']),
            'Ladakh' :pd.Series(['Ladakh','Jammu and Kashmir','Himachal Pradesh','Delhi']),
            'Andaman and Nicobar Islands' :pd.Series(['Andaman and Nicobar Islands','Delhi']),
            'Chhattisgarh' :pd.Series(['Chhattisgarh','Andhra Pradesh','Telangana','Odisha','Maharashtra','Uttar Pradesh','Madhya Pradesh','Delhi']),
            'Goa' :pd.Series(['Goa','','Maharashtra','Karnataka','Delhi']),
            'Puducherry' :pd.Series(['Puducherry','Tamil Nadu','Andhra Pradesh','Kerala','Delhi']),
            'Jharkhand' :pd.Series(['Jharkhand','Odisha','Bihar','West Bengal','Uttar Pradesh','Delhi']),
            'Manipur' :pd.Series(['Manipur','Nagaland','Mizoram','Assam','Delhi']),
            'Mizoram' :pd.Series(['Mizoram','Assam','Tripura','Manipur','Delhi']),
            'Arunachal Pradesh' :pd.Series(['Arunachal Pradesh','Assam','Nagaland','Delhi']),
            'Dadra and Nagar Haveli' :pd.Series(['Dadra and Nagar Haveli','Gujarat','Delhi']),
            'Tripura' :pd.Series(['Tripura','Assam','Mizoram','Delhi']),
            'Daman and Diu' :pd.Series(['Daman and Diu','Gujarat','Delhi']),
            'Lakshadweep' :pd.Series(['Lakshadweep','Delhi']),
            'Meghalaya' :pd.Series(['Meghalaya','Assam','Delhi']),
            'Nagaland' :pd.Series(['Nagaland','Assam Manipur','Delhi','Arunachal Pradesh']),
            'Sikkim' :pd.Series(['Sikkim','West Bengal','Delhi'])}

    state = pd.DataFrame(data)

    state_list = {1:'Maharashtra',2:'Tamil Nadu',3:'Delhi',4:'Telangana',5:'Rajasthan',6:'Kerala',7:'Uttar Pradesh',8:'Andhra Pradesh',9:'Madhya Pradesh',
                  10:'Karnataka',11:'Gujarat',12:'Haryana',13:'Jammu and Kashmir',14:'Punjab',15:'West Bengal',16:'Odisha',17:'Bihar',18:'Uttarakhand',19:'Assam',
                  20:'Chandigarh',21:'Himachal Pradesh',22:'Ladakh',23:'Andaman and Nicobar Islands',24:'Chhattisgarh',25:'Goa',26:'Puducherry',27:'Jharkhand',
                  28:'Manipur',29:'Mizoram',30:'Arunachal Pradesh',31:'Dadra and Nagar Haveli',32:'Tripura',33:'Daman and Diu',34:'Lakshadweep',35:'Meghalaya',
                  36:'Nagaland',37:'Sikkim'}


    def Statelist(statename):
          states = state[statename].dropna().unique().tolist()
          df= df[df['State'].isin(states)]
          df= df.drop_duplicates()
          df= df.pivot(index='Date', columns='State', values='Confirmed')
          states = list(df.columns)
          covid = df.reset_index('Date')
          jo=covid.to_json(date_format='iso',orient='index')
          # print (jo)
          return jo
          

    #print(state['Gujarat'].dropna().unique().tolist())
    #Fetch Value From User             
    #val = input("Enter State Code :\n1:Maharashtra\n2:Tamil Nadu\n3:Delhi\n4:Telangana\n5:Rajasthan\n6:Kerala\n7:Uttar Pradesh\n8:Andhra Pradesh\n9:Madhya Pradesh\n10:Karnataka\n11:Gujarat\n12:Haryana\n13:Jammu and Kashmir\n14:Punjab\n15:West Bengal\n16:Odisha\n17:Bihar\n18:Uttarakhand\n19:Assam\n20:Chandigarh\n21:Himachal Pradesh\n22:Ladakh\n23:Andaman and Nicobar Islands\n24:Chhattisgarh\n25:Goa\n26:Puducherry\n27:Jharkhand\n28:Manipur\n29:Mizoram\n30:Arunachal Pradesh\n31:Dadra and Nagar Haveli\n32:Tripura\n33:Daman and Diu\n34:Lakshadweep\n35:Meghalaya\n36:Nagaland\n37:Sikkim")
    # ||||||||ARGUMENTS||||||||| 
    states = state[(state_list[int(sid)])].dropna().unique().tolist()
    df = df[df['State'].isin(states)]

    # Section 3 - Restructuring our Data
    df= df.drop_duplicates()
    df= df.pivot(index='Date', columns='State', values='Confirmed')
    states = list(df.columns)
    covid = df.reset_index('Date')
    covid.set_index(['Date'], inplace=True)
    covid.columns = states
    
    # jo=json.dumps(covid.to_json(date_format='iso',orient='index'),separators=(',', ':'))
    jo=json.loads(covid.to_json(date_format='iso',orient='index'))
    # print(jo)
    return jo


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Covid19 API</h1>'''


@app.route('/api/v1/resources/covid19/all', methods=['GET'])
def api_all():
    global covid19
    return jsonify(covid19)

@app.route('/api/v1/resources/covid19/developed', methods=['GET'])
def api_developed():
    jsonify(covid19)
    if covid19['success'] == True:
        return jsonify(covid19['developed'])
    else:
        return "ERROR"  
     
    # return jsonify(covid19)    


@app.route('/api/v1/resources/covid19', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for book in covid19:
        if book['id'] == id:
            results.append(book)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)

app.run(host = '0.0.0.0',port="3030")