# Simple TCP DNS Resolver

This Python script resolves DNS records (A, AAAA, and CNAME) via TCP for a list of hostnames using multithreading. It works well with proxychains.

### Running the Script

The script resolves DNS records for a list of hostnames provided in an input file.

```bash
python3 dns_tcp_resolver.py <input_file> [options]
```

#### Options

- `-t`, `--threads`: Number of threads to use (default: 1)
- `-n`, `--dns-server`: DNS server IP to use (default: 8.8.8.8)
- `--timeout`: Timeout for DNS resolution in seconds (default: 5)
- `-v`, `--verbose`: Enable verbose mode
- `-o`, `--output-file`: Output file for results

### Examples

```bash
# Basic usage with default settings
python3 dns_tcp_resolver.py my_hostnames.txt

# Using multiple threads and specifying a different DNS server
python3 dns_tcp_resolver.py my_hostnames.txt -t 10 -n 1.1.1.1

# Enable verbose mode and save results to an output file
python3 dns_tcp_resolver.py my_hostnames.txt -v -o results.txt
