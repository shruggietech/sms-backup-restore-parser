# SMS Backup & Restore -- XML Format Technical Reference

An independent technical reference for the XML backup format produced by
SyncTech's **SMS Backup & Restore** Android application. All prose is original.
Field semantics are derived from the upstream XSD, official documentation, and
the XSL stylesheets distributed alongside the app.

---

## XML File Structure

SMS Backup & Restore generates two distinct types of XML backup files:

1. **Message backups** (SMS and MMS combined) use a `<smses>` root element.
2. **Call log backups** use a `<calls>` root element.

These are always separate files -- messages and calls never appear in the
same XML document.

### Message backup skeleton

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

### Call log backup skeleton

```xml
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<calls count="N">
  <call ... />
  <call ... />
</calls>
```

### Key structural points

- The `count` attribute on the root element reports the total number of child
  records in the file.
- Within `<smses>`, `<sms>` and `<mms>` elements can appear in any order --
  they are interleaved chronologically rather than grouped by type.
- `<mms>` elements always contain a `<parts>` wrapper (with one or more
  `<part>` children) and may contain an `<addrs>` wrapper (with one or more
  `<addr>` children). Note that the `<addrs>` element is present in real-world
  exports but is **not defined** in the official XSD schema.
- File sizes for long-term users routinely reach hundreds of megabytes to
  multiple gigabytes, primarily driven by base64-encoded MMS media.
- The XML declaration typically specifies `encoding='UTF-8'`.
- When the app preference "Add XSL Tag" is enabled, the XML includes an
  `<?xml-stylesheet?>` processing instruction referencing `sms.xsl` or
  `calls.xsl`, allowing browser-based rendering.
- When "Add Readable Date" is enabled, `readable_date` and `contact_name`
  optional attributes are populated on each record.

---

## SMS Fields

Each `<sms>` element is a self-closing tag whose entire payload is carried in
XML attributes. There are no child elements.

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `protocol` | `xs:unsignedByte` | No | Transport protocol identifier. Almost always `0` for standard SMS. | Typically `0` |
| `address` | `xs:string` | Yes | Phone number of the sender or recipient. Format varies by carrier and locale (may include country code, spaces, dashes, or leading `+`). | Any string |
| `date` | `xs:unsignedLong` | Yes | Timestamp of when the message was sent or received, expressed as milliseconds since the Unix epoch (1970-01-01 00:00:00 UTC). This is Java's standard epoch-millisecond representation. | Integer (as string in XML) |
| `type` | `xs:unsignedByte` | Yes | Direction and status of the message. | `1` = Received, `2` = Sent, `3` = Draft, `4` = Outbox, `5` = Failed, `6` = Queued |
| `subject` | `xs:string` | No | Message subject. For SMS this is almost universally the literal string `"null"`. | Any string, typically `"null"` |
| `body` | `xs:string` | Yes | Full text content of the message. May contain XML entity-escaped characters. | Any string |
| `toa` | `xs:string` | No | Type of Address for the destination. Typically unused and set to `"null"`. | Any string, typically `"null"` |
| `sc_toa` | `xs:string` | No | Type of Address for the service center. Typically unused and set to `"null"`. | Any string, typically `"null"` |
| `service_center` | `xs:string` | No | SMSC (Short Message Service Center) number that routed the message. Present for received messages, typically `"null"` for sent messages. | Phone number string or `"null"` |
| `read` | `xs:unsignedByte` | Yes | Whether the message has been read by the user. | `0` = Unread, `1` = Read |
| `status` | `xs:byte` | Yes | Delivery status of the message. | `-1` = None, `0` = Complete, `32` = Pending, `64` = Failed |
| `locked` | `xs:unsignedByte` | No | Whether the message is locked (protected from deletion). | `0` = Unlocked, `1` = Locked |
| `date_sent` | `xs:unsignedLong` | No | Timestamp when the message was sent, in epoch milliseconds. Distinct from `date`, which records the received time. May be `0` if unavailable. | Integer (as string) |
| `sub_id` | not in XSD | No | Identifies which SIM subscription (slot) handled the message. Format is device-dependent. | Small integers like `0`, `1`, `2` or a full SIM ICCID string |
| `readable_date` | `xs:string` | No | Human-friendly rendering of the `date` field. Only present when the "Add Readable Date" preference is enabled at backup time. Format depends on the user's configured date format setting. | e.g. `"Nov 20, 2006 6:21:00 PM"` |
| `contact_name` | `xs:string` | No | Display name from the phone's contacts database for the `address`. Only present when the preference is enabled and a matching contact exists. Unknown contacts appear as `"(Unknown)"`. | Any string |

---

## MMS Fields

Each `<mms>` element carries metadata as XML attributes and contains nested
`<parts>` and `<addrs>` child structures. The attribute set is significantly
larger than SMS because MMS inherits fields from the underlying Android MMS
provider database and the WAP MMS specification.

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `date` | `xs:unsignedLong` | Yes | Timestamp in epoch milliseconds for when the message was sent or received. | Integer (as string) |
| `ct_t` | `xs:string` | Yes | Top-level Content-Type of the MMS message. | Typically `"application/vnd.wap.multipart.related"` or `"application/vnd.wap.multipart.mixed"` |
| `msg_box` | `xs:unsignedByte` | Yes | Mailbox folder the message belongs to. Equivalent to SMS `type`. | `1` = Received, `2` = Sent, `3` = Draft, `4` = Outbox |
| `rr` | `xs:unsignedByte` | Yes | Read report request flag. Indicates whether a read receipt was requested. | Integer value |
| `sub` | `xs:string` | No | Subject line of the MMS message, if one was provided by the sender. | Any string |
| `read_status` | `xs:string` | Yes | Read status of the message in the MMS protocol sense. | String value |
| `address` | `xs:long` | Yes | Phone number of the primary sender or recipient. Note the XSD types this as `xs:long`, though in practice it contains phone number strings. | Phone number |
| `m_id` | `xs:string` | Yes | Globally unique Message-ID assigned by the MMS service center. Used for tracking and deduplication. | String identifier |
| `read` | `xs:unsignedByte` | Yes | Whether the user has read this message. | `0` = Unread, `1` = Read |
| `m_size` | `xs:string` | Yes | Total size of the MMS message in bytes, as reported by the carrier. | Numeric string |
| `m_type` | `xs:unsignedByte` | Yes | MMS message type code as defined by the WAP MMS specification (OMA-WAP-MMS). Indicates whether this is a send request, delivery indication, notification, etc. | Integer per MMS spec (e.g. `128` = Send Request, `132` = Retrieve Confirmation) |
| `text_only` | `xs:unsignedByte` | No | Flag indicating the MMS contains only text parts with no media attachments. | `0` = Has media, `1` = Text only |
| `retr_st` | `xs:string` | Yes | Retrieval status from the MMS server. | String value |
| `ct_cls` | `xs:string` | Yes | Content class of the MMS, defining the category of content allowed. | String value |
| `sub_cs` | `xs:string` | Yes | Character set encoding used for the subject field. | Charset identifier string |
| `ct_l` | `xs:string` | Yes | Content-Location URI where the MMS content can be retrieved. | URI string |
| `tr_id` | `xs:string` | Yes | Transaction ID used to correlate MMS protocol exchanges between client and server. | String identifier |
| `st` | `xs:string` | Yes | MMS delivery status. | String value |
| `m_cls` | `xs:string` | Yes | Message class (e.g. personal, advertisement, informational, auto). | String, typically `"personal"` |
| `d_tm` | `xs:string` | Yes | Delivery time. | String value |
| `retr_txt_cs` | `xs:string` | Yes | Character set for the retrieval text. | Charset identifier string |
| `d_rpt` | `xs:unsignedByte` | Yes | Delivery report request flag. Indicates whether a delivery confirmation was requested. | Integer value |
| `date_sent` | `xs:unsignedByte` | Yes | Timestamp when the message was sent. Note the XSD types this as `xs:unsignedByte`, which is likely an error in the schema -- real values are epoch milliseconds. | Integer (as string) |
| `seen` | `xs:unsignedByte` | Yes | Whether the message notification has been seen by the user (distinct from `read`). | `0` = Not seen, `1` = Seen |
| `v` | `xs:unsignedByte` | Yes | MMS specification version number used by this message. | Integer (e.g. `18` for version 1.2) |
| `exp` | `xs:string` | Yes | Expiry duration or timestamp for the message on the MMS server. | Numeric string (seconds) |
| `pri` | `xs:unsignedByte` | Yes | Priority level of the message. | `128` = Normal, `129` = High, `130` = Low (per MMS spec) |
| `resp_txt` | `xs:string` | Yes | Response text from the MMS server. | String value |
| `rpt_a` | `xs:string` | Yes | Report allowed flag. | String value |
| `locked` | `xs:unsignedByte` | Yes | Whether the message is locked against deletion. | `0` = Unlocked, `1` = Locked |
| `retr_txt` | `xs:string` | Yes | Retrieval text accompanying the message from the MMS server. | String value |
| `resp_st` | `xs:string` | Yes | Response status code from the MMS server. | String value |
| `sim_slot` | not in XSD | No | SIM card slot identifier. Not present in the official XSD but appears in real backups. | String value |
| `readable_date` | `xs:string` | No | Human-readable date string. Only present when the preference is enabled. | Formatted date string |
| `contact_name` | `xs:string` | No | Contact display name for the address. Only present when the preference is enabled. | Any string |

---

## MMS Part Fields

Each `<part>` element inside `<parts>` represents one component of a multipart
MMS message. A single MMS typically contains at minimum a SMIL layout
descriptor and one or more content parts (text, image, audio, video).

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `seq` | `xs:byte` | Yes | Sequence number controlling the order of parts within the message. Parts are ordered by ascending `seq` value. | Integer starting at `-1` or `0` |
| `ct` | `xs:string` | Yes | MIME content type of this part. Determines how the part should be interpreted. | See common content types below |
| `name` | `xs:string` | Yes | Name of the part, often derived from the original filename. May be `"null"` if not applicable. | Filename string or `"null"` |
| `chset` | `xs:string` | Yes | Character set encoding for text-based parts. Common values reference IANA charset numbers. | Charset number (e.g. `"106"` for UTF-8) or `"null"` |
| `cd` | `xs:string` | Yes | Content-Disposition header value. Indicates how the part should be presented. | `"null"` or disposition string |
| `fn` | `xs:string` | Yes | Filename for the part, as specified in the content headers. May differ from `name`. | Filename string or `"null"` |
| `cid` | `xs:string` | Yes | Content-ID used to reference this part from the SMIL layout or other parts. | Identifier string (e.g. `"<text_0>"`) |
| `cl` | `xs:string` | Yes | Content-Location providing a URI-like identifier for the part. | Location string (e.g. `"text_0.txt"`) |
| `ctt_s` | `xs:string` | Yes | Content-Type start parameter. Identifies the root part of the multipart message. | String or `"null"` |
| `ctt_t` | `xs:string` | Yes | Content-Type type parameter. Specifies the overall type of the multipart message. | String or `"null"` |
| `text` | `xs:string` | Yes | Text content of the part. Populated for `text/plain` parts, typically `"null"` for binary parts. | Message text or `"null"` |
| `data` | `xs:string` | No | Base64-encoded binary payload. Present for media parts (images, audio, video). Absent or empty for text-only parts. This field is the primary driver of large file sizes in MMS backups. | Base64 string |

### Common MMS content types

| MIME Type | Description |
|-----------|-------------|
| `application/smil` | SMIL (Synchronized Multimedia Integration Language) layout descriptor that controls how the MMS parts are presented. Nearly every MMS contains one. |
| `text/plain` | Plain text body of the message. The actual text is in the `text` attribute. |
| `image/jpeg` | JPEG photograph or image. Binary data in the `data` attribute. |
| `image/png` | PNG image. Binary data in the `data` attribute. |
| `image/gif` | GIF image (may be animated). Binary data in the `data` attribute. |
| `audio/mpeg` | MP3 or other MPEG audio. Binary data in the `data` attribute. |
| `audio/amr` | AMR audio recording, common for voice notes. |
| `video/mp4` | MP4 video. Binary data in the `data` attribute. |
| `video/3gpp` | 3GPP video, commonly recorded on older Android devices. |

---

## MMS Address Fields

Each `<addr>` element inside `<addrs>` identifies one participant in the MMS
conversation. Group MMS messages have multiple `<addr>` entries -- one for each
recipient and one for the sender.

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `address` | string | Yes | Phone number or email address of this participant. | Phone number or address string |
| `type` | integer | Yes | Role of this participant in the message. Values correspond to the PduHeaders constants in the Android telephony stack. | `129` = BCC, `130` = CC, `137` = From, `151` = To |
| `charset` | integer | Yes | Character set identifier for this address entry. | Integer (e.g. `106` for UTF-8) |

**Important:** The `<addrs>` wrapper and its `<addr>` children are present in
real-world backup exports but are **not defined** in the official XSD schema
published by SyncTech. Parsers should expect them to be present but must not
fail if they are absent.

---

## Call Log Fields

Each `<call>` element represents one entry in the phone's call history. Like
SMS, all data is carried in XML attributes with no child elements.

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `number` | string | Yes | Phone number associated with the call. May include country code prefixes. | Phone number string |
| `duration` | integer | Yes | Length of the call in seconds. `0` for missed or rejected calls. | Non-negative integer |
| `date` | unsigned long | Yes | Timestamp of the call in epoch milliseconds. | Integer (as string) |
| `type` | integer | Yes | Direction and disposition of the call. | `1` = Incoming, `2` = Outgoing, `3` = Missed, `4` = Voicemail, `5` = Rejected, `6` = Refused List |
| `presentation` | integer | No | Caller ID presentation mode. Indicates whether the remote party's identity was available. | `1` = Allowed, `2` = Restricted, `3` = Unknown, `4` = Payphone |
| `subscription_id` | string | No | Identifies the SIM subscription that handled the call. Format varies across devices -- some use simple indices (`0`, `1`, `2`) while others record the full SIM ICCID string. | Index integer or full SIM ID string |
| `readable_date` | string | No | Human-friendly date rendering. Only present when enabled in backup preferences. | Formatted date string |
| `contact_name` | string | No | Contact display name matched to the `number` field. Only present when enabled. | Any string |

**Note:** Call logs use a separate `<calls>` root element and are stored in
their own XML file. The official XSD only covers the `<smses>` root element.
The `<calls>` structure is confirmed by the `calls.xsl` stylesheet distributed
by SyncTech and by real-world backup files.

---

## Enum Reference Tables

### SMS type

| Value | Meaning |
|-------|---------|
| `1` | Received |
| `2` | Sent |
| `3` | Draft |
| `4` | Outbox |
| `5` | Failed |
| `6` | Queued |

### MMS msg_box

| Value | Meaning |
|-------|---------|
| `1` | Received |
| `2` | Sent |
| `3` | Draft |
| `4` | Outbox |

### Call type

| Value | Meaning |
|-------|---------|
| `1` | Incoming |
| `2` | Outgoing |
| `3` | Missed |
| `4` | Voicemail |
| `5` | Rejected |
| `6` | Refused List |

### MMS addr type

| Value | Meaning |
|-------|---------|
| `129` | BCC |
| `130` | CC |
| `137` | From |
| `151` | To |

### Call presentation

| Value | Meaning |
|-------|---------|
| `1` | Allowed (caller ID visible) |
| `2` | Restricted (caller ID withheld) |
| `3` | Unknown |
| `4` | Payphone |

### SMS status

| Value | Meaning |
|-------|---------|
| `-1` | None (no delivery status available) |
| `0` | Complete (delivered successfully) |
| `32` | Pending (delivery in progress) |
| `64` | Failed (delivery failed) |

### SMS/MMS read

| Value | Meaning |
|-------|---------|
| `0` | Unread |
| `1` | Read |

---

## Date Handling

All timestamp fields (`date`, `date_sent`) use **Java epoch milliseconds** --
the number of milliseconds elapsed since 1970-01-01 00:00:00 UTC.

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

In Excel, the formula `=(date_ms / 86400000) + 25569` converts to an Excel
date serial number (format the cell as date/time afterward).

### date vs date_sent

These are distinct fields serving different purposes:

- **`date`** -- the timestamp recorded by the local device. For received
  messages, this is when the message arrived. For sent messages, this is
  typically when the message was dispatched.
- **`date_sent`** -- the timestamp from the originating device or network.
  For received messages, this reflects when the sender actually sent it.
  May be `0` or absent if the network did not provide the information.

### readable_date

This optional field contains a locale-formatted date string generated at
backup time. The format is controlled by the app's "Readable Date Format"
setting and varies between users. The app added ISO 8601 as a format option
in v10.19.010. Because the format is user-configurable and locale-dependent,
parsers should prefer computing dates from the numeric `date` field rather
than parsing `readable_date`.

---

## MMS Structure Details

MMS messages have a nested structure that differs fundamentally from the flat
attributes of SMS and call log records.

### Parts

The `<parts>` wrapper contains one or more `<part>` elements representing the
individual components of the multipart message:

- **SMIL part** (`application/smil`): A layout descriptor that defines how the
  other parts should be arranged on screen. Present in virtually all MMS
  messages. The XSL viewer skips this part during display.
- **Text part** (`text/plain`): The human-readable text body. The text content
  is stored in the `text` attribute (not in the element's text content or
  `data` attribute).
- **Media parts** (images, audio, video): Binary content is base64-encoded in
  the `data` attribute. A single MMS may contain multiple media parts. These
  are the primary contributors to large backup file sizes.

### Addresses

The `<addrs>` wrapper contains `<addr>` elements enumerating all participants:

- For a standard two-party MMS, expect one `From` (type `137`) and one `To`
  (type `151`) address entry.
- For group MMS, there will be one `From` entry and multiple `To` entries
  (one per recipient).
- The `BCC` (type `129`) and `CC` (type `130`) types exist in the enum but
  are rarely encountered in practice.

### Example MMS structure

```xml
<mms date="1609459200000" msg_box="1" address="+15551234567"
     ct_t="application/vnd.wap.multipart.related" read="1" ...>
  <parts>
    <part seq="0" ct="application/smil" text="&lt;smil>...&lt;/smil>" />
    <part seq="0" ct="text/plain" text="Hello, world!" />
    <part seq="0" ct="image/jpeg" cl="image.jpg" data="[base64 data]" />
  </parts>
  <addrs>
    <addr address="+15559876543" type="137" charset="106" />
    <addr address="+15551234567" type="151" charset="106" />
  </addrs>
</mms>
```

---

## Known Quirks and Edge Cases

### Attribute presence varies by device

Field availability depends on the Android version, OEM customizations, and the
messaging app providing data to the Android content provider. Some attributes
documented in the XSD may be absent on certain devices, and undocumented
attributes (like `sim_slot` on MMS, `sub_id` on SMS) may appear on others.
Parsers should be tolerant of both missing and unexpected attributes.

### The string "null"

Android's content provider frequently stores SQL NULL values as the literal
four-character string `"null"` in XML attributes. This is **not** the absence
of the attribute -- it is a string value that reads `null`. Parsers must
distinguish between a missing attribute, an empty string `""`, and the literal
`"null"` string. Fields commonly affected: `subject`, `toa`, `sc_toa`,
`service_center`, `name`, `fn`, `cd`, `cid`, `cl`, `ctt_s`, `ctt_t`.

### readable_date format inconsistency

The `readable_date` field format is controlled by user preferences and varies
across backups. It may be locale-specific (`"Nov 20, 2006 6:21:00 PM"`),
ISO 8601 (`"2006-11-20T18:21:00"`), or any other format the user selected.
Do not rely on a specific format for parsing.

### contact_name availability

This field is only populated when the user had the "Add Contact Name"
preference enabled at backup time AND the phone number matched an entry in
the device's contact database. For numbers with no matching contact, the
value is `"(Unknown)"`. When the preference is disabled, the attribute is
entirely absent.

### Emoji and special characters

Message bodies (`body` for SMS, `text` for MMS parts) may contain emoji and
other multi-byte Unicode characters. Some XML viewers and parsers may not
render these correctly. The backup files use UTF-8 encoding, which handles
emoji natively, but downstream tools that assume ASCII or Latin-1 will
malfunction.

### XML entity escaping

Text content in `body` and `text` attributes uses standard XML entity escaping:

| Entity | Character |
|--------|-----------|
| `&amp;` | `&` (ampersand) |
| `&lt;` | `<` (less-than) |
| `&gt;` | `>` (greater-than) |
| `&quot;` | `"` (double quote) |
| `&#13;` | Carriage return |
| `&#10;` | Line feed |

Some T-Mobile firmware has been observed to produce `\r\n` (CRLF) line endings
within message bodies, while most Android devices use `\n` (LF) alone.

### sub_id and subscription_id format variance

The SIM identification fields (`sub_id` on SMS, `subscription_id` on call logs)
have inconsistent formats across devices:

- Some phones use simple zero-based indices: `0`, `1`, `2`
- Other phones record the full SIM ICCID or subscription identifier string
- Single-SIM devices may omit the field entirely

### MMS addr elements not in official XSD

The official XSD schema defines the `<parts>` structure within MMS but does
**not** include the `<addrs>` wrapper or its `<addr>` children. Despite this
omission, the `<addrs>` structure is consistently present in real backup files.
The addr type enum (129, 130, 137, 151) is documented in the official field
reference and must be supported.

### Call logs use a separate root element

The official XSD schema only describes the `<smses>` root element. Call log
backups use a `<calls>` root element that is **not covered by the XSD** but is
confirmed by the `calls.xsl` stylesheet and by real-world files. The `calls.xsl`
template matches on `calls/call`, confirming the element hierarchy.

### XSD type mismatches

Several XSD type declarations appear incorrect or overly restrictive compared
to real-world data:

- MMS `address` is typed as `xs:long` but contains phone number strings
  (including `+` prefixes and non-numeric characters)
- MMS `date_sent` is typed as `xs:unsignedByte` but holds epoch millisecond
  values in practice
- The root `count` attribute is typed as `xs:unsignedShort` (max 65535) but
  backup files routinely contain far more records

Parsers should treat all attribute values as strings and perform type
conversion explicitly rather than relying on the XSD type declarations.

### RCS / Advanced Messages

Newer versions of the app (v10.15.002+) support backing up RCS (Rich
Communication Services) messages on selected devices, specifically those using
Samsung Messages. These are stored within the same XML structure but may
include additional attributes or edge cases not covered by the original schema.

### Backup encryption (Pro)

The Pro version of the app (v10.05.301+) can compress and encrypt backups
using ZIP with AES-256 encryption. Encrypted backup files must be decrypted
before XML parsing. The underlying XML format remains the same after
decryption.
