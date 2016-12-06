#!/usr/bin/python3

import sys
from pathlib import Path

def main(argv):
    outData = []
    ret = 0
    hwmons = Path('/sys/class/hwmon')
    if (not hwmons.exists):
        ret = 3
        print("hwmon class does not exist in sysfs")
        return ret

    for hwmon in hwmons.iterdir():
        nameP = hwmon / 'name'
        with nameP.open() as read:
            nameStr = read.readline().strip()

        for temp in hwmon.glob('./temp[0-9]_input'):
            tempName = temp.name.split('_')[0]

            #Get current temperature
            with temp.open() as read:
                tempF = (int(read.readline().strip())/1000)
            tempStr = "%.1f" % tempF

            #Get label if exists
            labelP = temp.with_name(tempName +'_label')
            if (labelP.exists()):
                with labelP.open() as read:
                    labelStr = read.readline().strip()
            else:
                labelStr = tempName

            #Get critical tempereature if exists (WARNING in Nagios)
            critP = temp.with_name(tempName +'_crit')
            if (critP.exists()):
                with critP.open() as read:
                    critF = (int(read.readline().strip())/1000)
                critStr = "%.1f" % critF
                if (tempF > critF and ret < 1):
                    ret = 1
            else:
                critStr = ""

            #Get maximum temperature if exists (CRITICAL in Nagios)
            maxP = temp.with_name(tempName +'_max')
            if (maxP.exists()):
                with maxP.open() as read:
                    maxF = (int(read.readline().strip())/1000)
                maxStr = "%.1f" % maxF
                if (tempF > maxF and ret < 2):
                    ret = 2
            else:
                maxStr = ""

            if (sys.stdout.encoding == "UTF-8"):
                outData.append("\'"+nameStr+"-"+labelStr+"\'="+tempStr+"°C;"+critStr+";"+maxStr+";;")
            else:
                outData.append("\'"+nameStr+"-"+labelStr+"\'="+tempStr+"C;"+critStr+";"+maxStr+";;")

    print("Reading sensors successful|")
    for data in outData:
        print(data, end = " ")

    return ret

if __name__ == "__main__":
    main(sys.argv)
