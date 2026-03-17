# XML Format Reference

Technical reference for the XML backup format produced by SyncTech's SMS Backup & Restore Android application.

This page documents the structure and fields of the XML backup files that the parser consumes. It covers SMS, MMS, and call log records, enum values, date handling conventions, and known issues with the upstream XSD schema.

---

## File Structure

SMS Backup & Restore generates two distinct types of XML backup files:

- **Message backups** contain both SMS and MMS records under a `<smses>` root element.
- **Call log backups** contain call records under a `<calls>` root element.

Messages and calls are always in separate files; they never appear in the same XML document.

**Message backup skeleton:**

```xml
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<smses count="N">
  <sms ... />
  <mms ...>
    <parts>
      <part ... />
      <part ... />
    </parts>
    <addrs>
      <addr ... />
      <addr ... />
    </addrs>
  </mms>
  <sms ... />
  <!-- sms and mms elements may be interleaved freely -->
</smses>
```

**Call log backup skeleton:**

```xml
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<calls count="N">
  <call ... />
  <call ... />
</calls>
```

### Structural Notes

- The `count` attribute on the root element reports the total number of child records in the file.
- Within `<smses>`, `<sms>` and `<mms>` elements appear in any order, interleaved chronologically rather than grouped by type.
- Each `<mms>` element contains a `<parts>` wrapper (with one or more `<part>` children) and may contain an `<addrs>` wrapper (with one or more `<addr>` children).
- File sizes for long-term users routinely reach hundreds of megabytes to multiple gigabytes, primarily driven by base64-encoded MMS media.
- The XML declaration specifies `encoding='UTF-8'`.
- When the app preference "Add XSL Tag" is enabled, the XML includes an `<?xml-stylesheet?>` processing instruction referencing `sms.xsl` or `calls.xsl`, allowing browser-based rendering.
- When "Add Readable Date" is enabled, `readable_date` and `contact_name` optional attributes are populated on each record.

---

## SMS Fields

Each `<sms>` element is a self-closing tag whose entire payload is carried in XML attributes. There are no child elements.

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `protocol` | `xs:unsignedByte` | No | Transport protocol identifier. Almost always `0` for standard SMS. | Typically `0` |
| `address` | `xs:string` | Yes | Phone number of the sender or recipient. Format varies by carrier and locale (may include country code, spaces, dashes, or leading `+`). | Phone number string |
| `date` | `xs:unsignedLong` | Yes | Timestamp in Java epoch milliseconds. See [Date Handling](#date-handling). | Millisecond epoch integer |
| `type` | `xs:unsignedByte` | Yes | Message direction/disposition. See [SMS Type](#sms-type). | `1`–`6` |
| `subject` | `xs:string` | No | Message subject line. Rarely used for SMS; more common in MMS. | Any string or `"null"` |
| `body` | `xs:string` | Yes | Message text content. | Any string |
| `toa` | `xs:string` | No | Type of Address. BCD encoding indicator for the address field. | Typically `"null"` |
| `sc_toa` | `xs:string` | No | Service Center Type of Address. BCD encoding indicator for the SMSC number. | Typically `"null"` |
| `service_center` | `xs:string` | No | SMSC (Short Message Service Center) number that routed the message. | Phone number string or `"null"` |
| `read` | `xs:unsignedByte` | Yes | Read status. See [SMS/MMS Read](#smsmms-read). | `0` or `1` |
| `status` | `xs:byte` | Yes | Delivery status. See [SMS Status](#sms-status). | `-1`, `0`, `32`, `64` |
| `locked` | `xs:unsignedByte` | No | Whether the message is locked (protected from deletion). | `0` = unlocked, `1` = locked |
| `date_sent` | `xs:unsignedLong` | No | Sender-side timestamp in Java epoch milliseconds. See [date vs date_sent](#date-vs-date_sent). | Millisecond epoch integer or `0` |
| `sub_id` | `xs:string` | No | SIM subscription ID. Identifies which SIM handled the message on dual-SIM devices. | Index integer or full SIM ID string |
| `readable_date` | `xs:string` | No | Human-friendly date rendering. Present only when enabled in backup preferences. | Formatted date string |
| `contact_name` | `xs:string` | No | Contact display name matched to the `address` field. Present only when enabled. | Any string |

---

## MMS Fields

### MMS Record Attributes

Each `<mms>` element carries its metadata as XML attributes. Additionally, it contains nested `<parts>` and (optionally) `<addrs>` child elements. The MMS attribute set is substantially larger than SMS, reflecting the complexity of the MMS protocol (OMA MMS Encapsulation).

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `date` | `xs:unsignedLong` | Yes | Timestamp in Java epoch milliseconds. | Millisecond epoch integer |
| `ct_t` | `xs:string` | Yes | Content-Type of the MMS message. | Typically `"application/vnd.wap.multipart.related"` |
| `msg_box` | `xs:unsignedByte` | Yes | Message box (folder). See [MMS Message Box](#mms-message-box). | `1`–`4` |
| `rr` | `xs:unsignedByte` | Yes | Read report request. `128` = requested, `129` = not requested. | `128` or `129` |
| `read_status` | `xs:unsignedByte` | No | Read report status from the recipient side. | Integer |
| `address` | `xs:string` | Yes | Primary address (sender or recipient). On MMS, the XSD types this as `xs:long`, but real-world values contain phone number strings. | Phone number string |
| `m_id` | `xs:string` | Yes | Message ID assigned by the MMS gateway. Globally unique identifier for the MMS transaction. | URI-style string |
| `read` | `xs:unsignedByte` | Yes | Local read status. See [SMS/MMS Read](#smsmms-read). | `0` or `1` |
| `m_size` | `xs:string` | No | Message size in bytes as reported by the gateway. | Integer string |
| `m_type` | `xs:unsignedByte` | Yes | MMS message type (PDU type). `128` = send request, `132` = retrieve confirmation. | Integer |
| `retr_st` | `xs:unsignedByte` | No | Retrieve status code. `0` usually indicates success. | Integer |
| `ct_cls` | `xs:unsignedByte` | No | Content class. | Integer |
| `sub_cs` | `xs:string` | No | Subject character set (IANA number). | Integer string |
| `ct_l` | `xs:string` | No | Content-Location. URL from which the MMS content was retrieved. | URL string |
| `tr_id` | `xs:string` | Yes | Transaction ID for the MMS exchange. | String |
| `st` | `xs:unsignedByte` | No | Delivery status. | Integer |
| `m_cls` | `xs:string` | No | Message class (e.g., `"personal"`, `"advertisement"`). | String |
| `d_tm` | `xs:string` | No | Delivery time. | Epoch string |
| `retr_txt_cs` | `xs:unsignedByte` | No | Retrieve text character set. | Integer |
| `d_rpt` | `xs:unsignedByte` | No | Delivery report requested. `128` = requested. | `128` or `129` |
| `date_sent` | `xs:unsignedLong` | No | Sender-side timestamp. See [date vs date_sent](#date-vs-date_sent). | Millisecond epoch integer or `0` |
| `seen` | `xs:unsignedByte` | No | Whether the notification was seen. | `0` or `1` |
| `v` | `xs:unsignedByte` | No | MMS version. | Integer |
| `exp` | `xs:string` | No | Message expiry time. | Epoch string |
| `pri` | `xs:unsignedByte` | No | Priority. `128` = low, `129` = normal, `130` = high. | `128`, `129`, or `130` |
| `resp_txt` | `xs:string` | No | Response text from the gateway. | String |
| `rpt_a` | `xs:unsignedByte` | No | Report allowed flag. | Integer |
| `locked` | `xs:unsignedByte` | No | Locked status. | `0` or `1` |
| `retr_txt` | `xs:string` | No | Retrieve text. | String |
| `resp_st` | `xs:unsignedByte` | No | Response status from the gateway. | Integer |
| `text_only` | `xs:unsignedByte` | No | Whether the MMS contains only text parts (no media). | `0` or `1` |
| `sub` | `xs:string` | No | Message subject. | Any string |
| `sub_id` | `xs:string` | No | SIM subscription ID. | Index integer or full SIM ID string |
| `readable_date` | `xs:string` | No | Human-friendly date rendering. Present only when enabled. | Formatted date string |
| `contact_name` | `xs:string` | No | Contact display name. Present only when enabled. | Any string |

### MMS Part Fields

Each `<part>` element inside `<parts>` represents one component of the MMS message. A typical MMS contains at least a SMIL layout part and one content part (text or media).

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `seq` | `xs:byte` | Yes | Sequence number controlling the display order of parts. | Integer (starting from `-1` or `0`) |
| `ct` | `xs:string` | Yes | MIME content type of this part. | MIME type string (e.g., `"text/plain"`, `"image/jpeg"`) |
| `name` | `xs:string` | Yes | Part name, often derived from the original filename. | String or `"null"` |
| `chset` | `xs:string` | Yes | Character set as an IANA number (e.g., `"106"` for UTF-8). | Integer string or `"null"` |
| `cd` | `xs:string` | Yes | Content-Disposition header value. | String or `"null"` |
| `fn` | `xs:string` | Yes | Filename from content headers. | String or `"null"` |
| `cid` | `xs:string` | Yes | Content-ID for referencing this part from SMIL layout. | String or `"null"` |
| `cl` | `xs:string` | Yes | Content-Location identifier. | String or `"null"` |
| `ctt_s` | `xs:string` | Yes | Content-Type start parameter. Identifies the root part of the multipart message. | String or `"null"` |
| `ctt_t` | `xs:string` | Yes | Content-Type type parameter. Specifies the overall type of the multipart message. | String or `"null"` |
| `text` | `xs:string` | Yes | Text content of the part. Populated for `text/plain` parts; typically `"null"` for binary parts. | Message text or `"null"` |
| `data` | `xs:string` | No | Base64-encoded binary payload. Present for media parts (images, audio, video). This field is the primary driver of large file sizes in MMS backups. | Base64 string |

### Common MMS Content Types

| MIME Type | Description |
|-----------|-------------|
| `application/smil` | SMIL (Synchronized Multimedia Integration Language) layout descriptor controlling how MMS parts are presented. Nearly every MMS contains one. |
| `text/plain` | Plain text body of the message. The actual text is in the `text` attribute. |
| `image/jpeg` | JPEG photograph or image. Binary data in the `data` attribute. |
| `image/png` | PNG image. Binary data in the `data` attribute. |
| `image/gif` | GIF image (may be animated). Binary data in the `data` attribute. |
| `audio/mpeg` | MP3 or other MPEG audio. Binary data in the `data` attribute. |
| `audio/amr` | AMR audio recording, common for voice notes. |
| `video/mp4` | MP4 video. Binary data in the `data` attribute. |
| `video/3gpp` | 3GPP video, commonly recorded on older Android devices. |

### MMS Address Fields

Each `<addr>` element inside `<addrs>` identifies one participant in the MMS conversation. Group MMS messages have multiple `<addr>` entries, one for each recipient and one for the sender.

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `address` | string | Yes | Phone number or email address of this participant. | Phone number or address string |
| `type` | integer | Yes | Role of this participant in the message. Values correspond to the PduHeaders constants in the Android telephony stack. | `129` = BCC, `130` = CC, `137` = From, `151` = To |
| `charset` | integer | Yes | Character set identifier for this address entry. | Integer (e.g., `106` for UTF-8) |

!!! note
    The `<addrs>` wrapper and its `<addr>` children are present in real-world backup exports but are not defined in the official XSD schema published by SyncTech. Parsers should expect them to be present but not fail if they are absent.

---

## Call Log Fields

Each `<call>` element represents one entry in the phone's call history. Like SMS, all data is carried in XML attributes with no child elements.

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `number` | string | Yes | Phone number associated with the call. May include country code prefixes. | Phone number string |
| `duration` | integer | Yes | Length of the call in seconds. `0` for missed or rejected calls. | Non-negative integer |
| `date` | `xs:unsignedLong` | Yes | Timestamp in Java epoch milliseconds. See [Date Handling](#date-handling). | Millisecond epoch integer |
| `type` | integer | Yes | Call direction/disposition. See [Call Type](#call-type). | `1`–`6` |
| `presentation` | integer | Yes | Caller ID presentation status. See [Call Presentation](#call-presentation). | `1`–`4` |
| `subscription_id` | string | No | SIM subscription that handled the call. On dual-SIM devices, this distinguishes which line was used. | Index integer or full SIM ID string |
| `readable_date` | string | No | Human-friendly date rendering. Present only when enabled in backup preferences. | Formatted date string |
| `contact_name` | string | No | Contact display name matched to the `number` field. Present only when enabled. | Any string |

!!! note
    Call logs use a separate `<calls>` root element and are stored in their own XML file. The official XSD only covers the `<smses>` root element. The `<calls>` structure is confirmed by the `calls.xsl` stylesheet distributed by SyncTech and by real-world backup files.

---

## Enum Reference

### SMS Type

| Value | Meaning |
|-------|---------|
| `1` | Received |
| `2` | Sent |
| `3` | Draft |
| `4` | Outbox |
| `5` | Failed |
| `6` | Queued |

### SMS Status

| Value | Meaning |
|-------|---------|
| `-1` | None (no delivery status available) |
| `0` | Complete (delivered successfully) |
| `32` | Pending (delivery in progress) |
| `64` | Failed (delivery failed) |

### SMS/MMS Read

| Value | Meaning |
|-------|---------|
| `0` | Unread |
| `1` | Read |

### MMS Message Box

| Value | Meaning |
|-------|---------|
| `1` | Received |
| `2` | Sent |
| `3` | Draft |
| `4` | Outbox |

### MMS Address Type

| Value | Meaning |
|-------|---------|
| `129` | BCC |
| `130` | CC |
| `137` | From |
| `151` | To |

### Call Type

| Value | Meaning |
|-------|---------|
| `1` | Incoming |
| `2` | Outgoing |
| `3` | Missed |
| `4` | Voicemail |
| `5` | Rejected |
| `6` | Refused List |

### Call Presentation

| Value | Meaning |
|-------|---------|
| `1` | Allowed (caller ID visible) |
| `2` | Restricted (caller ID withheld) |
| `3` | Unknown |
| `4` | Payphone |

---

## Date Handling

### Epoch Format

All timestamp fields (`date`, `date_sent`) use Java epoch milliseconds: the number of milliseconds elapsed since 1970-01-01 00:00:00 UTC.

### Conversion

To obtain a standard Unix timestamp (seconds), divide by 1000:

```
unix_seconds = date_ms / 1000
```

To convert to an ISO 8601 string in Python:

```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(date_ms / 1000, tz=timezone.utc)
iso_str = dt.isoformat()
```

In Excel, the formula `=(date_ms / 86400000) + 25569` converts to an Excel date serial number (format the cell as date/time afterward).

### date vs date_sent

These are distinct fields serving different purposes:

- **`date`** is the timestamp recorded by the local device. For received messages, this is when the message arrived. For sent messages, this is typically when the message was dispatched.
- **`date_sent`** is the timestamp from the originating device or network. For received messages, this reflects when the sender actually sent it. The value may be `0` or absent if the network did not provide the information.

### readable_date

This optional field contains a locale-formatted date string generated at backup time. The format is controlled by the app's "Readable Date Format" setting and varies between users. Do not rely on this field for programmatic date operations; use the `date` epoch value instead.

### Computed date_iso Field

The parser injects a computed `date_iso` field (ISO 8601, UTC) derived from the `date` attribute on every record. This is a convenience field for human readability and tooling interoperability. It is not present in the upstream XML. Injection is enabled by default and can be suppressed with the `--no-date-iso` CLI flag.

---

## XSD Known Issues

### Missing Definitions

The official XSD does not define the `<addrs>` wrapper element or its `<addr>` children within `<mms>`. Despite this omission, the `<addrs>` structure is consistently present in real backup files. The addr type enum values (`129`, `130`, `137`, `151`) are documented in the official field reference and are supported by the parser.

The XSD only describes the `<smses>` root element. Call log backups use a `<calls>` root element that is not covered by the XSD but is confirmed by the `calls.xsl` stylesheet and by real-world files.

### Type Mismatches

Several XSD type declarations are incorrect or overly restrictive compared to real-world data:

| Field | XSD Type | Actual Behavior |
|-------|----------|-----------------|
| MMS `address` | `xs:long` | Contains phone number strings (including `+` prefixes and non-numeric characters). |
| MMS `date_sent` | `xs:unsignedByte` | Holds epoch millisecond values (large integers). |
| Root `count` | `xs:unsignedShort` (max 65,535) | Backup files routinely contain far more records. |

All attribute values should be treated as strings with explicit type conversion rather than relying on the XSD type declarations.

### RCS and Advanced Messages

Newer versions of the app (v10.15.002+) support backing up RCS (Rich Communication Services) messages on selected devices, specifically those using Samsung Messages. These are stored within the same XML structure but may include additional attributes or edge cases not covered by the original schema.

### Backup Encryption

The Pro version of the app (v10.05.301+) can compress and encrypt backups using ZIP with AES-256 encryption. Encrypted backup files must be decrypted before XML parsing. The underlying XML format remains the same after decryption.
