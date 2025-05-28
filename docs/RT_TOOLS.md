# Red Team Tools (RT Tools) Integration

This document describes the Red Team Tools integration added to CAI, bringing 130+ red team tools from the [loganbek/RedTeam-Tools](https://github.com/loganbek/RedTeam-Tools) collection.

## Overview

The RT Tools integration enhances CAI's red team agent with specialized tools across multiple attack phases:

- **Reconnaissance**: Directory/file brute forcing, DNS enumeration, SMB enumeration
- **Credential Access**: Hash identification and password cracking
- **All tools**: Provide JSON output, non-interactive execution, and proper error handling

## Tools Added

### Directory/File Brute Forcing

#### Gobuster
- `gobuster_dir_scan(target_url, wordlist, extensions, threads, status_codes)` - Fast directory/file discovery
- `gobuster_dns_scan(domain, wordlist, threads)` - DNS subdomain enumeration

#### Feroxbuster  
- `feroxbuster_scan(target_url, wordlist, extensions, threads, depth, status_codes)` - Fast content discovery in Rust
- `feroxbuster_recursive_scan(target_url, wordlist, extensions, max_depth)` - Recursive content discovery with smart filtering

### DNS Enumeration

#### DNSRecon
- `dnsrecon_standard_scan(domain)` - Standard DNS record enumeration
- `dnsrecon_bruteforce_scan(domain, wordlist)` - DNS subdomain brute forcing
- `dnsrecon_axfr_scan(domain)` - DNS zone transfer attempts  
- `dnsrecon_comprehensive_scan(domain)` - Multi-scan comprehensive enumeration

### SMB/Windows Enumeration

#### Enum4linux
- `enum4linux_basic_scan(target)` - Basic SMB enumeration (-a flag)
- `enum4linux_comprehensive_scan(target)` - Comprehensive SMB enumeration with verbose output
- `enum4linux_null_session_scan(target)` - Null session enumeration attempts

### Credential Access

#### Hashcat
- `hashcat_identify_hash(hash_value)` - Identify hash types by format/length
- `hashcat_crack_md5(hash_file, wordlist)` - Crack MD5 hashes
- `hashcat_crack_ntlm(hash_file, wordlist)` - Crack NTLM hashes  
- `hashcat_crack_sha1(hash_file, wordlist)` - Crack SHA1 hashes
- `hashcat_crack_sha256(hash_file, wordlist)` - Crack SHA256 hashes

## Usage Examples

### Directory Brute Forcing
```python
# Fast directory scan with common extensions
result = gobuster_dir_scan("http://target.com", extensions="php,html,txt")

# Recursive content discovery
result = feroxbuster_recursive_scan("http://target.com", max_depth=3)
```

### DNS Enumeration
```python
# Standard DNS enumeration
result = dnsrecon_standard_scan("target.com")

# Comprehensive DNS reconnaissance
result = dnsrecon_comprehensive_scan("target.com")
```

### SMB Enumeration
```python
# Basic SMB enumeration
result = enum4linux_basic_scan("192.168.1.100")

# Null session attempt
result = enum4linux_null_session_scan("192.168.1.100")
```

### Credential Access
```python
# Identify hash type
result = hashcat_identify_hash("5d41402abc4b2a76b9719d911017c592")

# Crack MD5 hashes
result = hashcat_crack_md5("/path/to/hashes.txt", "/usr/share/wordlists/rockyou.txt")
```

## Integration with Red Team Agent

All RT Tools are automatically available to the red team agent with the following features:

- **Non-interactive execution**: All tools run in batch mode suitable for automation
- **JSON output**: Structured results for easy parsing and analysis
- **Error handling**: Graceful handling of missing tools or network issues
- **Timeout management**: Proper timeout handling to prevent hanging
- **Session management**: Compatible with CAI's session system

## Tool Dependencies

The RT Tools require the following external tools to be installed:

- **gobuster**: Fast directory/file brute forcer
- **feroxbuster**: Fast content discovery tool written in Rust  
- **dnsrecon**: DNS enumeration script
- **enum4linux**: SMB enumeration tool
- **hashcat**: Advanced password recovery utility

When tools are not installed, the functions will return appropriate error messages indicating the missing dependencies.

## File Structure

```
cai/tools/
├── reconnaissance/
│   ├── gobuster_tool.py     # Directory/file brute forcing
│   ├── feroxbuster_tool.py  # Content discovery
│   ├── dnsrecon_tool.py     # DNS enumeration
│   └── enum4linux_tool.py   # SMB enumeration
└── credential_access/
    └── hashcat_tool.py      # Password cracking
```

## Security and Ethical Usage

These tools are intended for authorized penetration testing and security research only. Users must:

- Obtain proper authorization before scanning any targets
- Follow responsible disclosure practices
- Comply with all applicable laws and regulations
- Use tools only on systems you own or have explicit permission to test

## Contributing

To add new RT Tools:

1. Create the tool module following the existing patterns
2. Ensure non-interactive execution with JSON output
3. Add proper error handling and timeout management
4. Update the red team agent's function list
5. Document the new tools in this file