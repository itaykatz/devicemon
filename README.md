
# devicemon 

An API to pull a list of nearby devices by their MAC address.

Devicemon scan the nearby area for probrequest or any other wifi packages,
it then enrich this data with vendor names and filters our only mobile devices.
 
It is can be deployed on a Raspbian or any other Linux OS, in my cas I used Raspberry Pi 3 with Atheros AR9271 WiFi Adapter for monitoring.
I should support the below chipsets:
Atheros AR9271, Ralink RT3070, Ralink RT3572, or Ralink RT5572.


## Dependencies

- Python 3.6 
- Tshark (Wireshark commandline) [tshark](https://www.wireshark.org/docs/man-pages/tshark.html) 


## Run

The progran can be initiated by the bash script located at the bin directory.


## Usage

The program uses Flask to expose an API for getting the current nearby devices, 
after running the service, scan can be triggered and result will be returned by GET request:
http://<host_ip>/devices?scan_time=<time>

while <time> is the total scan time for the scanner to scan.


###  JSON Output

The GET request output is a JSON-formatted which consist of nearby devices, in example:
```bash
[
  {
    "MAC": "e8:b2:ac:de:65:09", 
    "RSSI": "-77", 
    "Vendor": "Apple, Inc.", 
    "scan_start_timestamp": "2018-12-27 19:59:14.422790", 
    "scan_stop_timestamp": "2018-12-27 19:59:15.423146"
  }, 
  {
    "MAC": "8c:85:90:58:7f:dd", 
    "RSSI": "-69", 
    "Vendor": "Apple, Inc.", 
    "scan_start_timestamp": "2018-12-27 19:59:14.422790", 
    "scan_stop_timestamp": "2018-12-27 19:59:15.423146"
  }, 
  {
    "MAC": "24:a2:e1:eb:e8:2a", 
    "RSSI": "-84", 
    "Vendor": "Apple, Inc.", 
    "scan_start_timestamp": "2018-12-27 19:59:14.422790", 
    "scan_stop_timestamp": "2018-12-27 19:59:15.423146"
  }
]
```

A higher rssi means closer. 


### Visualize 

The visualization and storage of data will be done with Logstash and an HTTP Poller plugin.
I used with a ELK Stack Docker while configuring Logstash pipe as follows:
```bash
input {
http_poller {
    # List of urls to hit
    # URLs can either have a simple format for a get request
    # Or use more complex HTTP features
    urls => {
      some_other_service => {
        method => "GET"
        url => "http://<host_ip>:80/devices?scan_time=60"
      }
    }
    # Maximum amount of time to wait for a request to complete
    request_timeout => 60
    # Decode the results as JSON
    schedule => { cron => "*/2 * * * * UTC"}
    codec => "json"
    # Store metadata about the request in this key
    metadata_target => "http_poller_metadata"
  }
}

filter {
        json{
            source => "message"
        }

output {
        elasticsearch {
                hosts => "elasticsearch:9200"
                index => "devicemon"
        }
}
```

This will fetch nearby devices every 2 minute, in this example a 60 second scan will be initiated periodically.
We would have the ability to see and visualize the devices at Kibana (will be presented).



How does it work?
==================

Devicemon sniff probe requests and 802.11 packets coming from nearby devices in a given amount of time.
The probe requests can be "sniffed" from a monitor-mode enabled WiFi adapter using `tshark`.
An acccurate count depend on scanning time.
