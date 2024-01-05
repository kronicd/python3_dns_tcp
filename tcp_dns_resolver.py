import argparse
import dns.query
import dns.message
import dns.rdatatype
import threading
import sys

print_lock = threading.Lock()

def resolve_dns_tcp(hostname, dns_server, timeout=5):
    try:
        responses = []
        record_types = [dns.rdatatype.A, dns.rdatatype.CNAME, dns.rdatatype.AAAA]
        
        for record_type in record_types:
            request = dns.message.make_query(hostname, record_type)
            response = dns.query.tcp(request, dns_server, timeout=timeout)
            responses.append(response)
        
        return responses
    except dns.exception.Timeout:
        print(f"Timeout occurred while resolving {hostname}")
        return [None] * len(record_types)
    except dns.exception.DNSException as e:
        print(f"Error resolving {hostname}: {e}")
        return [None] * len(record_types)

def resolve_hostnames(hostnames, dns_server, timeout, verbose=False, output_file=None):
    out_file = None
    if output_file:
        out_file = open(output_file, 'w')
    try:
        for hostname in hostnames:
            hostname = hostname.strip()
            resolved_data = resolve_dns_tcp(hostname, dns_server, timeout)
            if resolved_data:
                for response in resolved_data:
                    if response:
                        for answer in response.answer:
                            if answer.rdtype in [dns.rdatatype.A, dns.rdatatype.AAAA, dns.rdatatype.CNAME]:
                                if answer.items:
                                    for item in answer.items:
                                        if answer.rdtype == dns.rdatatype.A:
                                            ip_address = item.address
                                            record_type = "A"
                                        elif answer.rdtype == dns.rdatatype.AAAA:
                                            ip_address = item.address
                                            record_type = "AAAA"
                                        else:
                                            ip_address = item.to_text()
                                            record_type = "CNAME"
                                        result = f"{hostname}, {ip_address}, {record_type}"
                                        with print_lock:
                                            print(result)
                                            if out_file:
                                                out_file.write(f'{result}\n')
                                elif verbose:
                                    with print_lock:
                                        sys.stderr.write(f"No records found for {hostname}\n")
                    else:
                        if verbose:
                            with print_lock:
                                sys.stderr.write(f"Unable to resolve {hostname}\n")
    finally:
        if out_file:
            out_file.close()

def main():
    parser = argparse.ArgumentParser(description='DNS Resolver')
    parser.add_argument('input_file', help='Input file containing hostnames')
    parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads (default: 1)')
    parser.add_argument('-n', '--dns-server', default='8.8.8.8', help='DNS server IP (default: 8.8.8.8)')
    parser.add_argument('--timeout', type=float, default=5, help='Timeout for DNS resolution in seconds (default: 5)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    parser.add_argument('-o', '--output-file', help='Output file for results')
    args = parser.parse_args()

    with open(args.input_file, 'r') as file:
        lines = file.readlines()

    num_lines = len(lines)
    lines_per_thread = num_lines // args.threads

    thread_list = []
    for i in range(args.threads):
        start = i * lines_per_thread
        end = start + lines_per_thread if i < args.threads - 1 else num_lines
        thread = threading.Thread(target=resolve_hostnames, args=(lines[start:end], args.dns_server, args.timeout, args.verbose, args.output_file))
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

if __name__ == "__main__":
    main()
