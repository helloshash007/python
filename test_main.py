import os
import argparse
import json
import traceback
import subprocess
import glob
import shutil
from datetime import datetime

def readDataFromFile(path):
    try:
        with open(path, 'r') as f:
            data = f.read()
    except Exception as e:
        traceback.print_exc()
    return data

def processRawData(data):
    data = data.split("\n")
    data_len = len(data)
    hashmap = {}

    for i in range(int(data_len / 2)):
        try:
            hashmap[str(i)] = json.loads(data[i * 2].replace('=>', ':').replace('nil', 'null'))
        except Exception as e:
            traceback.print_exc()
    return hashmap

def searchForRecord(process_data, sp_acc_num, sp_acc_curr_code):
    result = {}
    count = 0
    for index, _map in process_data.items():
        for key, value in _map.items():
            if "line_type" in key:
                for record in _map[key]:
                    acc_num = record["account_number"]
                    acc_curr = record["account_currency"]
                    if acc_num == sp_acc_num and acc_curr == sp_acc_curr_code:
                        count = count + 1
                        result["customer_country"] = record["customer_country"]
                        result["customer_institution"] = record["customer_institution"]
                        result["customer_identifier"] = record["customer_identifier"]
    return result, count

def searchRecord(filepath, sp_acc_num, sp_acc_curr_code):
    raw_data = readDataFromFile(filepath)
    process_data = processRawData(raw_data)
    searchResult = searchForRecord(process_data, sp_acc_num, sp_acc_curr_code)
    return searchResult

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="path to Test file", required=True)
    parser.add_argument("--accNum", help="Query Account Number", required=True)
    parser.add_argument("--currCode", help="Query Currency Code", required=True)  # Corrected the argument name
    args = parser.parse_args()
    result, count = searchRecord(args.path, args.accNum, args.currCode)
    print(result)
    if count == 1:
        now = datetime.now()
        print(now)
        Cust_Ident = "".join([result["customer_country"], result["customer_institution"], result["customer_identifier"])
        print("Cust ID =", Cust_Ident)
        subprocess.call(['bash', '/home/cffadmin/cff/execution.sh', Cust_Ident])
    elif count == 0:  # Changed the condition from = to ==
        print("No Record Found")
        list_of_files = glob.glob('/opt/hsbc/CashAnalytics_Data01/gir_reponse/*')
        latest_file = max(list_of_files, key=os.path.getctime)
        print("Failed_FileName =", latest_file)
        print("Moving File to Failed Directory")
        shutil.move(latest_file, "/opt/habs/CashAnalytics_Data01/gir_failed/")
    else:
        print("Multiple Record Found")
        list_of_files = glob.glob('/opt/hsbc/CashAnalytics_Data01/gir_reponse/*')
        latest_file = max(list_of_files, key=os.path.getctime)
        print("Failed_FileName =", latest_file)
        print("Moving File to Failed Directory")
        shutil.move(latest_file, "/opt/hsks/CashAnalytics_Data01/gir_failed/")
