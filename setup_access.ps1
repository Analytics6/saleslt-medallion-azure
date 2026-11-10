$ErrorActionPreference = 'Stop'
# Run as the Azure account authorized to administer these resources.
$signedInObjectId = az ad signed-in-user show --query id -o tsv
$signedInName = az account show --query user.name -o tsv
az sql server ad-admin create -g keystoneade3 -s keystoneade3sqlsrvr --display-name $signedInName --object-id $signedInObjectId --query login

# Temporary single-client-IP access for sample setup and independent verification.
$setupClientIp = Invoke-RestMethod 'https://api.ipify.org'
az sql server firewall-rule create -g keystoneade3 -s keystoneade3sqlsrvr -n CodexMedallionSetup --start-ip-address $setupClientIp --end-ip-address $setupClientIp --query name

# Required for Data Factory managed-identity authentication to Databricks.
az role assignment create --assignee-object-id 64dec3f9-af47-443f-93b1-fe3a9f9145a2 --assignee-principal-type ServicePrincipal --role Contributor --scope /subscriptions/c2383fdd-26a3-44a8-9d61-2c7f2e1e08bf/resourceGroups/AMIT_Azure_retail/providers/Microsoft.Databricks/workspaces/azuredatabricks_retail_sales --query roleDefinitionId
