import os
import subprocess

desktop = os.path.join(os.environ.get('USERPROFILE', r'C:\Users\Zeke'), 'Desktop')
target = r'E:\Documents\GitHub\JESSICA\Launch_Jessica.bat'
workdir = r'E:\Documents\GitHub\JESSICA'
lnk_path = os.path.join(desktop, 'Jessica Mission Control.lnk')

vbs_content = f'''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{lnk_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target}"
oLink.WorkingDirectory = "{workdir}"
oLink.Description = "Jessica Sovereign AI Mission Control Desktop"
oLink.Save
'''

vbs_path = 'temp_create_shortcut.vbs'
with open(vbs_path, 'w', encoding='utf-8') as f:
    f.write(vbs_content)

res = subprocess.run(['cscript', '//nologo', vbs_path], capture_output=True, text=True)
if os.path.exists(vbs_path):
    os.remove(vbs_path)

if os.path.exists(lnk_path):
    print(f"SUCCESS: Desktop shortcut verified at: {lnk_path}")
else:
    print(f"Notice: Could not place shortcut directly on desktop. Launcher bat is ready at {target}")

