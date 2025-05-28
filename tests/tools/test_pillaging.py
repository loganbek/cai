"""
Tests for the pillaging tools module.
"""
import pytest
from cai.tools.pillaging import (
    extract_ip_addresses,
    extract_software_versions,
    extract_pii,
    extract_credentials,
    run_crackmapexec_and_parse
)


class TestExtractIPAddresses:
    """Test IP address extraction functionality."""
    
    def test_basic_ip_extraction(self):
        text = "Server is at 192.168.1.1 and backup at 10.0.0.1"
        ips = extract_ip_addresses(text)
        assert "192.168.1.1" in ips
        assert "10.0.0.1" in ips
        assert len(ips) == 2
    
    def test_no_ips_found(self):
        text = "No IP addresses here"
        ips = extract_ip_addresses(text)
        assert ips == []
    
    def test_duplicate_ips(self):
        text = "Server 192.168.1.1 and backup 192.168.1.1"
        ips = extract_ip_addresses(text)
        assert len(ips) == 1
        assert "192.168.1.1" in ips


class TestExtractSoftwareVersions:
    """Test software version extraction functionality."""
    
    def test_apache_version(self):
        text = "Running Apache/2.4.53 (Unix)"
        versions = extract_software_versions(text)
        assert "Apache" in versions
        assert versions["Apache"] == "2.4.53"
    
    def test_multiple_versions(self):
        text = "Apache/2.4.53 nginx/1.20.1 OpenSSH_8.2p1"
        versions = extract_software_versions(text)
        assert "Apache" in versions
        assert "nginx" in versions
        assert "OpenSSH" in versions
    
    def test_no_versions_found(self):
        text = "No software versions here"
        versions = extract_software_versions(text)
        assert versions == {}


class TestExtractPII:
    """Test PII extraction functionality."""
    
    def test_email_extraction(self):
        text = "Contact us at support@example.com"
        pii = extract_pii(text)
        assert "support@example.com" in pii["emails"]
    
    def test_phone_extraction(self):
        text = "Call us at +1-555-123-4567"
        pii = extract_pii(text)
        assert len(pii["phone_numbers"]) > 0
    
    def test_multiple_pii_types(self):
        text = """
        Email: admin@test.com
        Phone: (555) 123-4567
        Website: https://example.com
        """
        pii = extract_pii(text)
        assert len(pii["emails"]) > 0
        assert len(pii["phone_numbers"]) > 0
        assert len(pii["urls"]) > 0
    
    def test_no_pii_found(self):
        text = "Just some regular text without PII"
        pii = extract_pii(text)
        assert pii["emails"] == []
        assert pii["phone_numbers"] == []


class TestExtractCredentials:
    """Test credential extraction functionality."""
    
    def test_api_key_extraction(self):
        text = 'api_key = "sk-1234567890abcdef1234567890abcdef"'
        creds = extract_credentials(text)
        api_keys = [c for c in creds if c["type"] == "api_key"]
        assert len(api_keys) > 0
        assert "sk-1234567890abcdef1234567890abcdef" in api_keys[0]["value"]
    
    def test_bearer_token_extraction(self):
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        creds = extract_credentials(text)
        bearer_tokens = [c for c in creds if c["type"] == "bearer_token"]
        assert len(bearer_tokens) > 0
    
    def test_database_connection_extraction(self):
        text = "mysql://user:password@localhost/database"
        creds = extract_credentials(text)
        db_creds = [c for c in creds if c["type"] == "database_connection"]
        assert len(db_creds) > 0
        assert db_creds[0]["username"] == "user"
        assert db_creds[0]["password"] == "password"
    
    def test_aws_key_extraction(self):
        text = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
        creds = extract_credentials(text)
        aws_keys = [c for c in creds if c["type"] == "aws_access_key"]
        assert len(aws_keys) > 0
        assert "AKIAIOSFODNN7EXAMPLE" in aws_keys[0]["value"]
    
    def test_no_credentials_found(self):
        text = "Just some regular text without credentials"
        creds = extract_credentials(text)
        assert creds == []


class TestRunCrackMapExec:
    """Test CrackMapExec functionality."""
    
    def test_crackmapexec_not_available(self):
        # This should return an error since crackmapexec likely isn't installed
        result = run_crackmapexec_and_parse("127.0.0.1", "--timeout 5")
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()
        assert result["target"] == "127.0.0.1"
    
    def test_crackmapexec_invalid_target(self):
        # Test with an invalid target format
        result = run_crackmapexec_and_parse("", "")
        assert result["status"] == "error"


if __name__ == '__main__':
    pytest.main([__file__, "-v"])