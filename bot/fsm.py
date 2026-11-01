"""
ماژول ماشین وضعیت متناهی (FSM) برای دریافت چندمرحله‌ای اطلاعات، رهگیری پرونده و یادداشت اپراتور در ربات «کافی نت لیمو».
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class FSMState(BaseModel):
    """مدل نگهدارنده وضعیت جاری مکالمه کاربر یا اپراتور."""
    user_id: int
    step: str  # IDLE | FIELD_INPUT | CONFIRMATION | AWAITING_TRACKING_CODE | OPERATOR_NOTE
    service_code: Optional[str] = None
    field_keys: List[str] = Field(default_factory=list)
    current_field_index: int = 0
    collected_data: Dict[str, Any] = Field(default_factory=dict)
    # فیلدهای ویژه مدارک پیوست
    collected_docs: List[Dict[str, Any]] = Field(default_factory=list)
    # فیلدهای ویژه مدیریت اپراتور
    order_id: Optional[int] = None
    target_status: Optional[str] = None
    # فیلدهای ویژه ثبت یادآور
    reminder_title: Optional[str] = None
    # فیلدهای ویژه شرایط مسکن و انتخاب شاهد
    terms_accepted: bool = False
    witness_choice: Optional[str] = None

    def step_back(self) -> bool:
        """بازگشت به مرحله قبلی در فرآیند مرحله‌ای ثبت درخواست."""
        if self.step == "CONFIRMATION":
            self.step = "FIELD_INPUT"
            if self.field_keys:
                self.current_field_index = len(self.field_keys) - 1
                last_key = self.field_keys[self.current_field_index]
                self.collected_data.pop(last_key, None)
            return True
        elif self.step == "FIELD_INPUT":
            if self.current_field_index > 0:
                prev_key = self.field_keys[self.current_field_index - 1]
                self.collected_data.pop(prev_key, None)
                self.current_field_index -= 1
                return True
            return False
        return False


class FSMManager:
    """مدیریت وضعیت‌های موقت کاربران و اپراتورها در حافظه."""

    def __init__(self):
        self._states: Dict[int, FSMState] = {}

    def get_state(self, user_id: int) -> Optional[FSMState]:
        """دریافت وضعیت فعلی کاربر."""
        return self._states.get(user_id)

    def start_order_flow(self, user_id: int, service_code: str, field_keys: List[str]) -> FSMState:
        """آغاز چرخه ثبت سفارش چندمرحله‌ای برای یک خدمت مشخص."""
        state = FSMState(
            user_id=user_id,
            step="FIELD_INPUT",
            service_code=service_code,
            field_keys=field_keys,
            current_field_index=0,
            collected_data={}
        )
        self._states[user_id] = state
        return state

    def start_tracking_flow(self, user_id: int) -> FSMState:
        """آغاز چرخه استعلام کد رهگیری."""
        state = FSMState(
            user_id=user_id,
            step="AWAITING_TRACKING_CODE"
        )
        self._states[user_id] = state
        return state

    def start_operator_note_flow(self, user_id: int, order_id: int, target_status: str) -> FSMState:
        """آغاز چرخه ثبت توضیحات یا نقص توسط اپراتور."""
        state = FSMState(
            user_id=user_id,
            step="OPERATOR_NOTE",
            order_id=order_id,
            target_status=target_status
        )
        self._states[user_id] = state
        return state

    def start_chat_flow(self, user_id: int) -> FSMState:
        """آغاز چرخه گفتگوی زنده با پشتیبانی (چت دوطرفه)."""
        state = FSMState(
            user_id=user_id,
            step="IN_SUPPORT_CHAT"
        )
        self._states[user_id] = state
        return state

    def start_reminder_flow(self, user_id: int) -> FSMState:
        """آغاز چرخه ثبت یادآور جدید تقویمی."""
        state = FSMState(
            user_id=user_id,
            step="REMINDER_TITLE"
        )
        self._states[user_id] = state
        return state

    def step_back(self, user_id: int) -> bool:
        """انتقال وضعیت کاربر به یک گام قبل‌تر در FSM."""
        state = self.get_state(user_id)
        if state:
            return state.step_back()
        return False

    def set_reminder_title(self, user_id: int, title: str) -> Optional[FSMState]:
        """ثبت عنوان یادآور و انتقال به مرحله دریافت تاریخ شمسی."""
        state = self.get_state(user_id)
        if state and state.step == "REMINDER_TITLE":
            state.reminder_title = title.strip()
            state.step = "REMINDER_DATE"
            return state
        return None

    def clear_state(self, user_id: int) -> None:
        """پاکسازی و ریست کردن وضعیت کاربر."""
        self._states.pop(user_id, None)
