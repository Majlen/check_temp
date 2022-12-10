#!/usr/bin/python3

import sys, argparse
from pathlib import Path

def main(argv):
    outData = []
    ret = 0
    retMsg = "OK: Average temperature is "
    avg = 0
    count = 0
    minTemp = "0.0"


    parser = argparse.ArgumentParser()
    parser.add_argument('-m', help='minimum temperature')
    args = (parser.parse_args())

    if args.m:
        minTemp = "%.1f" % float(args.m)

    hwmons = Path('/sys/class/hwmon')
    if (not hwmons.exists()):
        print("UNKNOWN: Cannot find hwmon class in sysfs")
        return 3
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
                
                #skip zero values
                if not tempStr:
                    continue

                #Get label if exists
                labelP = temp.with_name(tempName + '_label')
                if (labelP.exists()):
                    with labelP.open() as read:
                        labelStr = read.readline().strip()
                else:
                    labelStr = tempName

                #Get critical tempereature if exists (WARNING in Nagios)
                (maxStr, maxF) = getTemp(temp, tempName + '_crit')
                if (maxF > 0 and tempF > maxF and ret < 1):
                    retMsg = "WARNING: " + nameStr + "-" + labelStr + " is higher than its threshold "
                    ret = 1

                #Get maximum temperature if exists (CRITICAL in Nagios)
                (critStr, critF) = getTemp(temp, tempName + '_max')
                if (critF > 0 and tempF > critF and ret < 2):
                    retMsg = "CRITICAL: " + nameStr + "-" + labelStr + " is higher than its threshold "
                    ret = 2

                outData.append("\'"+nameStr+"-"+labelStr+"\'="+tempStr+";"+critStr+";"+maxStr+";"+minTemp+";"+maxStr)

                avg = (avg * count + tempF) / (count + 1)
                count = count + 1

    if (sys.stdout.encoding == "UTF-8"):
        print(retMsg + "%.1f" % avg +  "°C|", end = "")
    else:
        print(retMsg + "%.1f" % avg +  "C|", end = "")
    for data in outData:
        print(data, end = " ")

    sys.exit(ret)

def resolveName(curName, path):
    parts = path.parts
    #print(parts)

    if (parts[3] == "virtual"):
        return curName + "." + path.name.replace("hwmon", "")
    elif (parts[3] == "platform"):
        return parts[4]
    elif (parts[3].startswith("pci")):
        if 'usb' in parts[5]:
            pciAddr = parts[5]
        else:
            pciAddr = parts[5].split(':', 1)
        return curName + ".pci" + pciAddr[1]
    else:
        return curName + ".TODO.unknown"

def getTemp(curPath, tempName):
    if (curPath != tempName):
        tempPath = curPath.with_name(tempName)
    else:
        tempPath = curPath

    tempString = ""
    tempFloat = 0
    if (tempPath.exists()):
        with tempPath.open() as read:
            try:
                tempFloat = (int(read.readline().strip())/1000)
            except OSError as e:
                    #print("Sensor {} has no value {}".format(tempPath,e))
                    return (False,float(0))

        tempString = "%.1f" % tempFloat

    return (tempString, tempFloat)

if __name__ == "__main__":
    main(sys.argv)
