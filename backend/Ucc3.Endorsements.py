function Sign-Endorsement {
    param (
        [Parameter(Mandatory)]
        [object]$Endorsement,

        [Parameter(Mandatory)]
        [string]$EndorserName
    )

    $cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -like "*$EndorserName*" }

    if (-not $cert) {
        throw "Certificate for '$EndorserName' not found."
    }

    $rsa = $cert.GetRSAPrivateKey()
    if (-not $rsa) {
        throw "Unable to access RSA private key. Ensure the certificate is exportable and uses RSA."
    }

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Endorsement.ToString())
    $sig = $rsa.SignData($bytes, [System.Security.Cryptography.HashAlgorithmName]::SHA256, [System.Security.Cryptography.RSASignaturePadding]::Pkcs1)

    $Endorsement.Signature = [Convert]::ToBase64String($sig)
    return $Endorsement
}