import sys
import os
import re
import pandas as pd

def main():
    log_file_path = get_log_file_path_from_cmd_line()
    if not log_file_path:
        return

    port_traffic_dict = tally_port_traffic(log_file_path)
    for port_number, traffic_count in port_traffic_dict.items():
        if traffic_count >= 100:
            generate_port_traffic_report(log_file_path, port_number)
    
    generate_invalid_user_report(log_file_path)
    generate_source_ip_log(log_file_path, '220.195.35.40')

def get_log_file_path_from_cmd_line():
    if len(sys.argv) < 2:
        print("Error: The file path of gateway log is not provided!")
        return None
    if not os.path.exists(sys.argv[1]):
        print("Error: File does not exist!")
        return None
    return sys.argv[1]

def filter_log_by_regex(log_file, regex, ignore_case=True, print_summary=False, print_records=False):
    """Gets a list of records in a log file that match a specified regex."""
    records = []
    captured_data = []
    flags = re.IGNORECASE if ignore_case else 0

    with open(log_file, 'r') as file:
        for line in file:
            match = re.search(regex, line, flags)
            if match:
                records.append(line.strip())
                captured_data.append(match.groups())

    if print_records:
        for record in records:
            print(record)

    if print_summary:
        match_type = "case-insensitive" if ignore_case else "case-sensitive"
        print(f"The number of records matched in the log file is {len(records)} and {match_type} regex matching was performed.")
    
    return records, captured_data

def tally_port_traffic(log_file):
    regex = r'DPT=(\d+) '
    captured_data_list = filter_log_by_regex(log_file, regex)[1]
    port_traffic_dict = {}

    for port, in captured_data_list:
        if port in port_traffic_dict:
            port_traffic_dict[port] += 1
        else:
            port_traffic_dict[port] = 1
    
    return port_traffic_dict

def generate_port_traffic_report(log_file, port_number):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_file_path = os.path.join(script_dir, f'destination_port_{port_number}_report.csv')

    regex = rf'(.*?\d) (.*?) .*?SRC=(.*?) DST=(.*?) .*?SPT=(.*?) DPT={port_number} '
    captured_data = filter_log_by_regex(log_file, regex)[1]
    
    report_data = {
        'Date': [],
        'Time': [],
        'Source IP address': [],
        'Destination IP address': [],
        'Source port no': [],
        'Destination port no': []
    }

    for entry in captured_data:
        report_data['Date'].append(entry[0])
        report_data['Time'].append(entry[1])
        report_data['Source IP address'].append(entry[2])
        report_data['Destination IP address'].append(entry[3])
        report_data['Source port no'].append(entry[4])
        report_data['Destination port no'].append(port_number)

    df = pd.DataFrame(report_data)
    df.to_csv(report_file_path, index=False, mode='a')

def generate_invalid_user_report(log_file):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_file_path = os.path.join(script_dir, 'invalid_users.csv')

    regex = r'(.*?\d) (\d+:\d+:\d+).*? user (.*?) from (\d+\.\d+\.\d+\.\d+)'
    captured_data = filter_log_by_regex(log_file, regex)[1]

    report_data = {
        'Date': [],
        'Time': [],
        'Username': [],
        'IP Address': []
    }

    for entry in captured_data:
        report_data['Date'].append(entry[0])
        report_data['Time'].append(entry[1])
        report_data['Username'].append(entry[2])
        report_data['IP Address'].append(entry[3])

    df = pd.DataFrame(report_data)
    df.to_csv(report_file_path, index=False, mode='a')

def generate_source_ip_log(log_file, ip_address):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sanitized_ip = ip_address.replace('.', '_')
    log_file_path = os.path.join(script_dir, f'source_ip_{sanitized_ip}.log')

    regex = rf'.*?SRC={ip_address} '
    matching_lines = filter_log_by_regex(log_file, regex)[0]

    with open(log_file_path, 'a') as file:
        for line in matching_lines:
            file.write(line + '\n')

if __name__ == '__main__':
    main()