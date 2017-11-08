#!/usr/bin/python3

import sys
from pathlib import Path

def main(argv):
    outData = []
    ret = 0
    retMsg = "OK: Average temperature is "
    avg = 0
    count = 0
    hwmons = Path('/sys/class/hwmon')
    if (not hwmons.exists):
        ret = 3
        retMsg = "UNKNOWN: Cannot find hwmon class in sysfs"
    else:
        for hwmon in hwmons.iterdir():
            if (not (hwmon / 'name').exists()):
                #At least one driver (i5k_amb I am looking at you) does not put temperature data
                #into hwmon directory and puts them into its root instead. In hwmon class, symlink
                #called device goes to the module's root directory.
                hwmon = hwmon / 'device'

            #Get name
            nameP = hwmon / 'name'
            with nameP.open() as read:
                nameStr = resolveName(read.readline().strip(), hwmon.resolve())


            for temp in hwmon.glob('./temp*_input'):
                tempName = temp.name.split('_')[0]

                #Get current temperature
                (tempStr, tempF) = getTemp(temp, temp)

                #Get label if exists
                labelP = temp.with_name(tempName + '_label')
                if (labelP.exists()):
                    with labelP.open() as read:
                        labelStr = read.readline().strip()
                else:
                    labelStr = tempName

                #Get critical tempereature if exists (WARNING in Nagios)
                (maxStr, maxF) = getTemp(temp, tempName + '_crit')
                if (tempF > maxF and ret < 1):
                    retMsg = "WARNING: " + nameStr + "-" + labelStr + " is higher than its threshold"
                    ret = 1

                #Get maximum temperature if exists (CRITICAL in Nagios)
                (critStr, critF) = getTemp(temp, tempName + '_max')
                if (tempF > critF and ret < 2):
                    retMsg = "CRITICAL: " + nameStr + "-" + labelStr + " is higher than its threshold"
                    ret = 2

                outData.append("\'"+nameStr+"-"+labelStr+"\'="+tempStr+";"+critStr+";"+maxStr+";;"+maxStr)

                avg = (avg * count + tempF) / (count + 1)
                count = count + 1

    if (sys.stdout.encoding == "UTF-8"):
        print(retMsg + "%.1f" % avg +  "°C|", end = "")
    else:
        print(retMsg + "%.1f" % avg +  "C|", end = "")
    for data in outData:
        print(data, end = " ")

    return ret

def resolveName(curName, path):
    parts = path.parts
    #print(parts)

    if (parts[3] == "virtual"):
        return curName + "." + path.name.replace("hwmon", "")
    elif (parts[3] == "platform"):
        return parts[4]
    elif (parts[3].startswith("pci")):
        pciAddr = parts[5].split(':', 1)
        return curName + ".pci" + pciAddr[1]
    else:
        return curName + ".TODO.unknown"

def getTemp(curPath, tempName):
    if (curPath != tempName):
        tempPath = curPath.with_name(tempName)
    else:
        tempPath = curPath

    if (tempPath.exists()):
        with tempPath.open() as read:
            tempFloat = (int(read.readline().strip())/1000)
        tempString = "%.1f" % tempFloat
    else:
        tempString = ""
        tempFloat = 0
    return (tempString, tempFloat)

if __name__ == "__main__":
    main(sys.argv)
