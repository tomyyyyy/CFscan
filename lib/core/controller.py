import os
import sys
from lib.core.pretreament import pretreament
from lib.core.Fingerprint import Fingerprint
from lib.core.nmap_scan import nmap_scan


class Controller(object):
    def __init__(self, script_path, arguments):
        self.script_path = script_path
        self.arguments = arguments

        if self.arguments.options.file != None:
            os.system(F"zmap -w {self.arguments.options.file} -p 80 -B 100M -o {self.script_path}/json/zmap_ip.txt")
            nm = nmap_scan(F"{self.script_path}/json/zmap_ip.txt")
            nm.scan_thread()

            

                



            # os.system(F"zgrab2 --input-file={self.script_path}/json/zmap_ip.txt --output-file={self.script_path}/json/zgrab2.json --senders=1000   {self.arguments.options.protocol}")

            # pre = pretreament(self.script_path)
            # result = Fingerprint(self.script_path)


        else:
            print("must support file parameters")
            sys.exit(0)



