"""Tests for sms_backup_parser.models enum constants."""

from sms_backup_parser.models import (
    SMS_TYPES,
    MMS_MSG_BOX,
    CALL_TYPES,
    ADDR_TYPES,
    PRESENTATION_TYPES,
    SMS_STATUS,
)


class TestEnumsNonEmpty:
    """All enum dicts contain entries."""

    def test_sms_types_non_empty(self):
        assert len(SMS_TYPES) > 0

    def test_mms_msg_box_non_empty(self):
        assert len(MMS_MSG_BOX) > 0

    def test_call_types_non_empty(self):
        assert len(CALL_TYPES) > 0

    def test_addr_types_non_empty(self):
        assert len(ADDR_TYPES) > 0

    def test_presentation_types_non_empty(self):
        assert len(PRESENTATION_TYPES) > 0

    def test_sms_status_non_empty(self):
        assert len(SMS_STATUS) > 0


class TestSmsTypes:
    """SMS_TYPES has keys '1' through '6'."""

    def test_keys(self):
        for k in ("1", "2", "3", "4", "5", "6"):
            assert k in SMS_TYPES


class TestCallTypes:
    """CALL_TYPES has keys '1' through '6'."""

    def test_keys(self):
        for k in ("1", "2", "3", "4", "5", "6"):
            assert k in CALL_TYPES


class TestMmsMsgBox:
    """MMS_MSG_BOX has keys '1' through '4'."""

    def test_keys(self):
        for k in ("1", "2", "3", "4"):
            assert k in MMS_MSG_BOX


class TestAddrTypes:
    """ADDR_TYPES has keys for BCC, CC, From, To."""

    def test_keys(self):
        for k in ("129", "130", "137", "151"):
            assert k in ADDR_TYPES
