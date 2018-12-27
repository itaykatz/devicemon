import datetime as dt
import subprocess
import pandas
import pandas as pd
from flask import current_app
from settings.all_oui import oui
from settings.cellphone_titles import cellphone_titles


class TsharkScanner(object):
    def __init__(self, tmp_path, interface):
        self.tmp_path = tmp_path
        self.interface = interface

    def scan(self, scan_time, in_file=None):
        """Monitor wifi signals to count the number of people around you"""
        if not in_file:
            current_app.logger.info("No file given")

            if not self.interface:
                current_app.logger.error("No interface was selected")
                exit(1)

            self.tshark_scan(scan_time)
            scan_output = self.tshark_parse(self.tmp_path)

        else:
            scan_output = self.tshark_parse(in_file)

        # parse string to columns in DataFrame
        devices_df = pandas.DataFrame(scan_output.decode('utf-8').split('\n'))[0].str.split("\t", n=2, expand=True)

        # add Vendors to df
        devices_vendor_df = self.tshark_add_vendor(devices_df)

        # Filter only cellphone vendors
        only_mobile_vendor_df = devices_vendor_df[devices_vendor_df['Vendor'].isin(cellphone_titles)]

        # add timestamps
        only_mobile_vendor_df = only_mobile_vendor_df.assign(
            scan_start_timestamp=str(dt.datetime.now() - dt.timedelta(seconds=scan_time)))
        only_mobile_vendor_df = only_mobile_vendor_df.assign(scan_stop_timestamp=str(dt.datetime.now()))

        only_mobile_vendor_dict = only_mobile_vendor_df.to_dict(orient='records')
        return only_mobile_vendor_dict

    def tshark_scan(self, scan_time):
        current_app.logger.info("Initiating tshark...")

        command = ['tshark',
                   '-I',
                   '-i', self.interface,
                   '-a', 'duration:' + str(scan_time),
                   '-w', self.tmp_path]
        current_app.logger.info("Running command: {}".format(command))
        run_tshark = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = run_tshark.communicate()
        current_app.logger.error(stderr)
        current_app.logger.info(stdout)
        return stdout, stderr

    @staticmethod
    def tshark_parse(tshark_file):
        current_app.logger.info("Start parsing...")
        command = ['tshark',
                   '-r', tshark_file,
                   '-T', 'fields',
                   '-e', 'wlan.sa',
                   '-e', 'wlan.bssid',
                   '-e', 'radiotap.dbm_antsignal'
                   ]

        run_tshark = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        current_app.logger.info("Running command: {}".format(command))
        stdout, stderr = run_tshark.communicate()
        current_app.logger.error(stderr)
        current_app.logger.info(stdout)
        return stdout

    @staticmethod
    def tshark_add_vendor(devices_df):
        current_app.logger.error("Enriching data with Vendor names...")
        splitted_devices_df = pd.DataFrame()
        splitted_devices_df['MAC'] = devices_df[0]
        splitted_devices_df['MAC'].replace('', pd.np.nan, inplace=True)
        splitted_devices_df['RSSI'] = devices_df[2].str.split(",", n=1, expand=True)[0]

        splitted_devices_df.dropna(subset=['MAC'], inplace=True)
        splitted_devices_df.drop_duplicates(subset='MAC', keep="last", inplace=True)
        splitted_devices_df.loc[splitted_devices_df['MAC'].notnull(), 'MAC_Prefix'] = splitted_devices_df['MAC'].str[
                                                                                      0:8]

        all_oui_df = pd.DataFrame(list(oui.items()), columns=['MAC_Prefix', 'Vendor'])
        devices_vendor_df = pd.merge(splitted_devices_df, all_oui_df, on='MAC_Prefix')
        devices_vendor_df.drop(columns=['MAC_Prefix'], inplace=True)

        return devices_vendor_df
