# Active Directory Group Policy Objects (GPO) Architecture

## Processing Order: LSDOU
Group policies in Active Directory are applied strictly in the **LSDOU** order:
1. **Local**: Local machine policy on the workstation.
2. **Site**: Policies linked to the physical Active Directory Site.
3. **Domain**: Domain-level policies affecting all objects in the domain.
4. **Organizational Unit (OU)**: OU-specific policies (innermost OU has the final override precedence).

## Enforcement & Blocking
- **Enforced (No Override)**: Overrides any downstream conflicting settings, taking absolute priority regardless of OU nesting.
- **Block Inheritance**: Stops upstream Site, Domain, and parent OU policies from applying to this OU, unless those policies are marked as Enforced.
- **Loopback Processing**: Crucial for Terminal Servers/RDS. Replaces or merges computer policy settings over the logged-in user's user-configuration settings.

## Diagnostic Commands
- `gpupdate /force`: Forces immediate re-application of user and computer policies without waiting for standard 90-minute refresh.
- `gpresult /r`: Displays Applied and Filtered-Out GPOs for current user and computer.
- `gpresult /h gpreport.html`: Generates complete visual HTML audit report of applied registry keys.
