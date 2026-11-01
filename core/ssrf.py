"""
ماژول حفاظت در برابر حملات جعل درخواست سمت سرور (SSRF Shield) و DNS Rebinding.
این ماژول قبل از ارسال هرگونه درخواست HTTP، نشانی URL، پروتکل، پورت، دامنه و کلیه IPهای
حل‌شده از طریق DNS را ارزیابی و مسیرهای شبکه داخلی و سرویس‌های محلی را مسدود می‌کند.
"""

import socket
import ipaddress
from urllib.parse import urlsplit
from typing import Tuple, Optional, Sequence


ALLOWED_SCHEMES = ("http", "https")
ALLOWED_DEFAULT_PORTS = (80, 443, 8080, 8443)


def is_ip_dangerous(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """بررسی اینکه آیا نشانی IP متعلق به شبکه‌های خصوصی، لوپ‌بک، متادیتای ابری یا رزروشده است."""
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped

    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def is_safe_url(
    url: str,
    resolve_dns: bool = True,
    allowed_ports: Sequence[int] = ALLOWED_DEFAULT_PORTS
) -> Tuple[bool, str]:
    """
    اعتبارسنجی امنیتی URL قبل از برقراری اتصال شبکه.
    - مسدودسازی پروتکل‌های غیرمجاز (مانند file://, gopher://, ftp://).
    - مسدودسازی پورت‌های مشکوک یا نامتعارف.
    - حل نام دامنه و مسدودسازی قطعی در صورت نگاشت به IPهای داخلی (مانند 127.0.0.1، 169.254.169.254، شبکه محلی).
    """
    if not url or not isinstance(url, str):
        return False, "نشانی وب واردنشده یا نامعتبر است."

    clean_url = url.strip()
    try:
        parsed = urlsplit(clean_url)
    except Exception as exc:
        return False, f"خطا در تجزیه URL: {exc}"

    # ۱. اعتبارسنجی پروتکل (Scheme)
    scheme = (parsed.scheme or "").lower()
    if scheme not in ALLOWED_SCHEMES:
        return False, f"پروتکل «{scheme}» مجاز نیست؛ فقط http و https پشتیبانی می‌شوند."

    # ۲. اعتبارسنجی میزبان (Hostname)
    hostname = parsed.hostname
    if not hostname:
        return False, "نام میزبان (Host) در URL یافت نشد."

    hostname_clean = hostname.strip().lower()

    # مسدودسازی صریح localhost و عبارات شناخته‌شده لوپ‌بک
    if hostname_clean in ("localhost", "localhost.localdomain", "broadcasthost"):
        return False, "دسترسی به میزبان محلی (localhost) اکیداً ممنوع است."

    # ۳. اعتبارسنجی پورت
    port = parsed.port
    if port is None:
        port = 443 if scheme == "https" else 80

    if port not in allowed_ports:
        return False, f"پورت {port} در فهرست پورت‌های مجاز ({list(allowed_ports)}) نیست."

    # ۴. بررسی در صورتی که Hostname مستقیماً یک IP باشد
    try:
        direct_ip = ipaddress.ip_address(hostname_clean)
        if is_ip_dangerous(direct_ip):
            return False, f"اتصال به نشانی IP داخلی یا غیرمجاز ({direct_ip}) مسدود گردید."
        return True, "نشانی مستقیم IP مجاز و امن است."
    except ValueError:
        # نام دامنه است نه IP مستقیم
        pass

    # ۵. تحلیل DNS Rebinding و بررسی کلیه IPهای متناظر دامنه
    if resolve_dns:
        try:
            addr_info = socket.getaddrinfo(hostname_clean, port, proto=socket.IPPROTO_TCP)
            if not addr_info:
                return False, f"امکان حل نام دامنه {hostname_clean} وجود ندارد."

            for _, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                resolved_ip = ipaddress.ip_address(ip_str)
                if is_ip_dangerous(resolved_ip):
                    return False, f"دامنه {hostname_clean} به نشانی داخلی و ناامن {ip_str} نگاشت شده است (SSRF Blocked)."

        except socket.gaierror:
            return False, f"خطای DNS: دامنه {hostname_clean} یافت نشد."
        except Exception as exc:
            return False, f"خطای ناشناخته در بررسی امنیتی DNS: {exc}"

    return True, "نشانی وب امن و مجاز است."
