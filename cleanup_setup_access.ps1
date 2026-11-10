$ErrorActionPreference = 'Stop'
# Remove only the temporary setup rules; retain operational Azure service access.
az sql server firewall-rule delete -g keystoneade3 -s keystoneade3sqlsrvr -n CodexMedallionSetup
az sql server firewall-rule delete -g AMIT_Azure_retail -s sqlserverretai -n CodexMedallionSetup
