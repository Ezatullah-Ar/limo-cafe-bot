"""
آزمون‌های خودکار سپر امنیتی SSRF Shield و مهار DNS Rebinding (core/ssrf.py)
"""

import unittest
from core.ssrf import is_safe_url, is_ip_dangerous
import ipaddress


class TestSSRF(unittest.TestCase):
    """مجموعه آزمون‌های راستی‌آزمایی امنیت شبکه و جلوگیری از حملات SSRF."""

    def test_dangerous_ip_detection(self):
        """آزمون شناسایی کلیه دامنه‌های IP خصوصی، متادیتا، لوپ‌بک و رزروشده."""
        bad_ips = [
            "127.0.0.1",
            "127.0.1.1",
            "10.0.0.1",
            "10.255.255.255",
            "172.16.0.1",
            "172.31.255.255",
            "192.168.0.1",
            "192.168.1.100",
            "169.254.169.254",  # AWS/GCP/Azure Cloud Metadata IP
            "0.0.0.0",
            "::1",
            "fe80::1",
            "::ffff:127.0.0.1",  # IPv4-mapped IPv6
            "::ffff:169.254.169.254",
        ]

        for ip_str in bad_ips:
            ip = ipaddress.ip_address(ip_str)
            self.assertTrue(is_ip_dangerous(ip), f"IP {ip_str} باید به عنوان ناامن علامت‌گذاری شود.")

        good_ips = ["8.8.8.8", "1.1.1.1", "4.2.2.4"]
        for ip_str in good_ips:
            ip = ipaddress.ip_address(ip_str)
            self.assertFalse(is_ip_dangerous(ip), f"IP عمومی {ip_str} باید مجاز باشد.")

    def test_unsafe_schemes_blocked(self):
        """آزمون مسدودسازی پروتکل‌های خطرناک غیر از HTTP/HTTPS."""
        unsafe_urls = [
            "file:///etc/passwd",
            "file:///C:/Windows/win.ini",
            "gopher://127.0.0.1:70/",
            "ftp://anonymous@ftp.example.com/",
            "dict://127.0.0.1:11211/",
            "data:text/html,test",
            "javascript:alert(1)"
        ]
        for url in unsafe_urls:
            is_safe, reason = is_safe_url(url, resolve_dns=False)
            self.assertFalse(is_safe)
            self.assertIn("مجاز نیست", reason)

    def test_localhost_and_internal_ip_urls_blocked(self):
        """آزمون مسدودسازی نشانی‌های متصل به localhost یا IPهای شبکه داخلی."""
        internal_urls = [
            "http://localhost/",
            "http://localhost:8080/admin",
            "http://127.0.0.1/",
            "http://127.0.0.1:8000/metrics",
            "http://192.168.1.1/router-config",
            "http://10.0.0.5:80/db",
            "http://169.254.169.254/latest/meta-data/",
            "http://[::1]/",
        ]
        for url in internal_urls:
            is_safe, reason = is_safe_url(url, resolve_dns=False)
            self.assertFalse(is_safe, f"نشانی {url} باید مسدود شود.")

    def test_disallowed_ports_blocked(self):
        """آزمون مسدودسازی پورت‌های پرخطر یا غیروب (مانند SSH, Redis, MySQL)."""
        bad_port_urls = [
            "http://example.com:22/",     # SSH
            "http://example.com:25/",     # SMTP
            "http://example.com:6379/",   # Redis
            "http://example.com:3306/",   # MySQL
            "http://example.com:27017/",  # MongoDB
        ]
        for url in bad_port_urls:
            is_safe, reason = is_safe_url(url, resolve_dns=False)
            self.assertFalse(is_safe)
            self.assertIn("پورت", reason)

    def test_safe_public_url_allowed(self):
        """آزمون تایید نشانی‌های عمومی استاندارد و معتبر."""
        safe_urls = [
            "https://www.sanjesh.org/",
            "https://emt.medu.ir/",
            "http://example.com/"
        ]
        for url in safe_urls:
            is_safe, _ = is_safe_url(url, resolve_dns=False)
            self.assertTrue(is_safe)


if __name__ == "__main__":
    unittest.main()
