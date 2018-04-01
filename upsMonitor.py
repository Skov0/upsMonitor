# skovdev ups monitor ups
# gets and updates influxdb with current power usage and load of ups.
import time;
from selenium import webdriver;
import argparse;
from influxdb import InfluxDBClient;
import datetime;
import random;

# influxdb connection
USER = 'USERNAME'
PASSWORD = 'PASSWD'
DBNAME = 'upsdb'

def main():
    print("UPSMonitor v0.1 started...");
    # start loop
    startLoop(120);

def startLoop(runInterval):
    while True:
        #time.sleep(runInterval);
        print("[!] Querying 192.168.50.25:8888 for UPS data...");

        # get content
        try:
            browser = webdriver.Firefox(executable_path="C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python36-32\\Scripts\\geckodriver.exe");
            browser.get('http://192.168.50.25:8888/0');
            activePW = browser.find_element_by_id('out-w').text;
            activeLoad = browser.find_element_by_id('out-load').text;
            browser.quit();

            # print it - debug
            #print(activePW);
            #print(activeLoad);

            # strip text
            activePW = activePW.split(": ")[1].split("K")[0];
            activeLoad = activeLoad.split(": ")[1];

            # calc kilowatthours
            floatactivePW = float(activePW);
            kwHresult = (floatactivePW * 1000) * 24 / 1000;
            price = kwHresult * 43.24;
            priceDKK = price / 100;
            priceDKK = str(round(priceDKK, 1));
            priceDKK = priceDKK + " DKK";

            # update influxDB
            uploadinfluxDB(priceDKK, activeLoad);
        except:
            continue;

        time.sleep(runInterval);

def uploadinfluxDB(priceDKK, activeLoad):
    print("[!] Updating influxDB...");

    host='192.168.50.12';
    port=8086;
    time = now = datetime.datetime.today();

    json_body = [
        {
            "measurement": "ups_pw",
            "tags": {
                "host": "ups"
            },
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "fields": {
                "power": priceDKK
            }
        }
    ]

    json_body2 = [
        {
            "measurement": "ups_load",
            "tags": {
                "host": "ups"
            },
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "fields": {
                "load": activeLoad
            }
        }
    ]
 
    client = InfluxDBClient(host, port, USER, PASSWORD, DBNAME)
 
    retention_policy = 'awesome_policy'
    client.create_retention_policy(retention_policy, '3d', 3, default=True)
 
    client.write_points(json_body);
    client.write_points(json_body2);
    print("[!] Updated influxDB.. Values: %s, %s" % (str(priceDKK), str(activeLoad)))


if __name__ == "__main__":
    main();