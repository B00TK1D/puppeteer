while($true) {
    $env:HostIP = (
        Get-NetIPConfiguration |
        Where-Object {
            $_.IPv4DefaultGateway -ne $null -and
            $_.NetAdapter.Status -ne "Disconnected"
        }
    ).IPv4Address.IPAddress
    netsh trace start capture=yes IPv4.Address=$env:HostIP tracefile=C:\temp\capture.etl
    Start-Sleep 10
    netsh trace stop
}