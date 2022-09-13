# Download and install python for pytia

$source = "https://www.python.org/ftp/python/3.10.7/python-3.10.7-amd64.exe"
$downloads = (New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path
$destination = "$($downloads)\python-3.10.7-amd64.exe"

Invoke-WebRequest -Uri $source -OutFile $destination

Start-Process -FilePath $destination -ArgumentList "/passive PrependPath=1 Include_doc=0 Include_test=0 SimpleInstall=1"
