"""
ماژول استخراج و تحلیل هوشمند اطلاعات فیش بانکی (services/ocr.py)
سامانه «کافی نت لیمو».
مسئول پردازش متن رسید، استخراج شماره کارت، مبلغ، تاریخ تراکنش و شماره پیگیری.
"""

import re
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Optional, Any

logger = logging.getLogger("ocr")

PERSIAN_NUMS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_NUMS = "٠١٢٣٤٥٦٧٨٩"
ENGLISH_NUMS = "0123456789"
DIGIT_TRANS = str.maketrans(PERSIAN_NUMS + ARABIC_NUMS, ENGLISH_NUMS + ENGLISH_NUMS)


def normalize_digits(text: Optional[str]) -> str:
    """تبدیل کلیه ارقام فارسی و عربی به معادل استاندارد انگلیسی."""
    if not text:
        return ""
    return str(text).translate(DIGIT_TRANS)


def extract_receipt_data(text_corpus: str) -> Dict[str, Optional[str]]:
    """
    استخراج شماره کارت، تاریخ، ساعت، مبلغ و کد رهگیری از متن فیش بانکی.
    """
    normalized = normalize_digits(text_corpus)
    clean_text = " ".join(normalized.replace("\n", " ").replace("\r", " ").split())

    # ۱. جستجوی شماره کارت ۱۶ رقمی (عادی یا ستاره‌دار)
    card_pattern = r'\b\d{4}[\s\-\*]{6,14}\d{4}\b|\b(?:\d[\s\-]*){16}\b'
    card_match = re.search(card_pattern, clean_text)
    card_number = card_match.group(0).replace(" ", "").replace("-", "") if card_match else None

    # ۲. جستجوی تاریخ و ساعت تراکنش
    date_match = re.search(r'\b(140\d[/-]\d{1,2}[/-]\d{1,2}|202\d[/-]\d{1,2}[/-]\d{1,2})\b', clean_text)
    time_match = re.search(r'\b([0-1]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?\b', clean_text)
    tx_date = date_match.group(0) if date_match else None
    tx_time = time_match.group(0) if time_match else None

    # ۳. جستجوی مبلغ واریزی (ریال یا تومان)
    amount_match = re.search(r'\b\d{1,3}(?:[,\.،]\d{3})+(?:\s*(?:ریال|تومان))?\b|\b\d{5,9}\s*(?:ریال|تومان)\b', clean_text)
    amount_str = None
    if amount_match:
        raw_amt = amount_match.group(0)
        # فقط ارقام را نگه می‌داریم
        digits_only = re.sub(r'[^\d]', '', raw_amt)
        if digits_only:
            amount_str = f"{int(digits_only):,}"

    # ۴. شماره پیگیری / کد ارجاع / شناسه مرجع
    trace_match = re.search(r'(?:پیگیری|ارجاع|مرجع|رهگیری|trace|ref)[:\s#]*([A-Za-z0-9]{4,15})', clean_text, re.IGNORECASE)
    trace_number = trace_match.group(1) if trace_match else None

    return {
        "card_number": card_number,
        "date": tx_date,
        "time": tx_time,
        "amount": amount_str,
        "trace_number": trace_number,
        "raw_extracted": clean_text[:200] if clean_text else None
    }


def perform_ocr_space(
    file_url: str,
    api_key: str = "K84523321588957",
    opener: Optional[Any] = None,
    timeout: float = 12.0
) -> Dict[str, Any]:
    """ارسال لینک تصویر فیش به OCR.space API جهت استخراج متن."""
    ocr_endpoint = (
        f"https://api.ocr.space/parse/imageurl?apikey={api_key}"
        f"&url={file_url}&language=ara&isOverlayRequired=false&OCREngine=2"
    )
    req = urllib.request.Request(
        url=ocr_endpoint,
        headers={"User-Agent": "LimoCafeBot-OCR/1.0"}
    )
    try:
        call = opener.open if opener else urllib.request.urlopen
        with call(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if not data.get("IsErroredOnProcessing") and data.get("ParsedResults"):
                extracted_text = data["ParsedResults"][0].get("ParsedText", "")
                return {
                    "ok": True,
                    "text": extracted_text,
                    "parsed": extract_receipt_data(extracted_text)
                }
            return {"ok": False, "error": data.get("ErrorMessage", ["OCR processing failed"])}
    except Exception as exc:
        logger.warning("OCR request failed: %s", exc)
        return {"ok": False, "error": str(exc)}
