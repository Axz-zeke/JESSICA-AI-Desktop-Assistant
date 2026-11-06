# Windows Server Active Directory and GPO Hardening

## Active Directory Tiering Architecture
Enterprise security separates identities into administrative boundaries:
- **Tier 0:** Domain Controllers, PKI, Azure AD Connect, Domain Admins.
- **Tier 1:** Member Servers, Hypervisors, Storage, Service Accounts.
- **Tier 2:** Workstations, End-User Accounts, Helpdesk.

## Key Group Policy Objects (GPOs) for Hardening
1. **Kerberos & NTLM Hardening:** Restrict NTLMv1, enforce NTLMv2 and Kerberos AES-128/256 encryption.
2. **LAPS (Local Administrator Password Solution):** Automatically rotates unique local admin passwords stored encrypted in AD attributes.
3. **SMBv1 Deprecation:** Enforce SMB 3.1.1 encryption and SMB signing via GPO.

## CLI Health Checks
```powershell
dcdiag /v /c /d /e /s:DC01
repadmin /replsummary
repadmin /showrepl * /csv > repl_status.csv
Get-ADDomainController -Filter * | Select-Object Name, IPv4Address, OperatingSystem
```
