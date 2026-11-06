# Biometric and RFID Access Control Systems

## Controller Architecture & Wiegand Protocol
Access control systems utilize centralized microcontrollers (e.g. ZKTeco, HID VertX, Paxton) communicating over RS-485 or OSDP (Open Supervised Device Protocol) to biometric optical/capacitive fingerprint scanners and RFID badge readers.

## Wiegand Interface Signal Lines
- **DATA0 (Green):** Low pulse represents binary 0.
- **DATA1 (White):** Low pulse represents binary 1.
- Standard 26-bit Wiegand frame: 1 parity bit, 8 facility code bits, 16 card number bits, 1 parity bit.

## Fail-Safe vs Fail-Secure Electric Locks
- **Fail-Safe (Maglocks):** Requires power to remain locked; unlocks during power cut for life safety egress (fire compliance).
- **Fail-Secure (Electric Strikes):** Stays locked during power loss; requires backup UPS or mechanical key bypass.
