"""
esxi-wmWare-Backup-Creator

@author Marc Sahib

"""

import re

from VM import VM
from OnlineVM import OnlineVM

"""
Parst die Informationen aus der Datei "runningVMsList.txt". 


"""
def getOnlineVMs(path):
    with open(path) as file:
        listProcesses = []
        isVm = False

        vmWareProcess = OnlineVM()

        for line in file:

            if not line.startswith("   "):
                isVm = True

            if isVm:

                if not line.startswith("   ") and not line.startswith("\n"):
                    vmWareProcess.name = line.split()[0]
                if line.__contains__("World ID"):
                    vmWareProcess.worldId = line.split(":")[1].split()[0]
                if line.__contains__("Process ID"):
                    vmWareProcess.processId = line.split(":")[1].split()[0]
                if line.__contains__("VMX Cartel ID"):
                    vmWareProcess.vmxCartelId = line.split(":")[1].split()[0]
                if line.__contains__("UUID"):
                    vmWareProcess.uuId = line.split(":")[1].split()[0]
                if line.__contains__("Display Name"):
                    vmWareProcess.displayName = line.split(":")[1].split()[0]
                if line.__contains__("Config File"):
                    vmWareProcess.configFile = line.split(":")[1].split()[0]
                    isVm = False
                    listProcesses.append(vmWareProcess)
                    vmWareProcess = OnlineVM()
        return listProcesses


"""
Parst die Informationen aus der Datei "allVMsList.txt"

"""
def getAllVMs(path):
    with open(path) as file:
        listOfflineVMs = []

        vm = VM()

        for line in file:
            #line = line.strip()  # preprocess line
            if line[0].isdigit():

                line = re.sub('  +', ';', line)
                attributes = line.split(";")

                vm.vmId      = attributes[0]
                vm.name      = attributes[1]
                vm.file      = attributes[2]
                vm.guestOs   = attributes[3]
                vm.version   = attributes[4]
                listOfflineVMs.append(vm)
                vm = VM()

        return listOfflineVMs


def printVMs(VMs):
    cnt = 1
    for vm in VMs:
        print(str(cnt) + " : " + vm.name)
        cnt += 1


def waitForUserInputToGetVMSelection(VMs):
    print("Enter id to Backup:")
    try:
        selectedVM = int(input())
        if not 0 < selectedVM <= len(VMs):
            waitForUserInputToGetVMSelection(VMs)
        else:
            print("VM \"" + VMs[selectedVM - 1].name + "\" selected.")
            for vm in VMs:
                if vm.name == VMs[selectedVM - 1].name:
                    return vm
    except:
        print("Enter a valid id from list.")
        waitForUserInputToGetVMSelection(VMs)

def isSelectedVMRunning(selectedVm, onlineVMWs):
    isVMRunning = False

    for onlineVm in onlineVMWs:
        #Wenn die ausgewaehlte VM online ist, erhaelt sie die Infos des laufenden Prozesses.
        if selectedVm.name == onlineVm.name:
            selectedVm.configFile = onlineVm.configFile
            selectedVm.displayName = onlineVm.displayName
            selectedVm.processId = onlineVm.processId
            selectedVm.uuId = onlineVm.uuId
            selectedVm.vmxCartelId = onlineVm.vmxCartelId
            selectedVm.worldId = onlineVm.worldId
            isVMRunning = True

    return isVMRunning


if __name__ == '__main__':

    onlineVMWs = getOnlineVMs("runningVMsList.txt")
    # ToDo: Implementiere Erstellung der runningVMsLis.txt auf esxi-Host
    # Datei wird durch den folgenden Befehl auf dem esxi-Host erzeugt:
    # $ esxcli vm process list >> runningVMsList.txt

    allVMs = getAllVMs("allVMsList.txt")
    # ToDo: Implementiere Erstellung der allVMsLis.txt auf esxi-Host
    # Datei wird durch den folgenden Befehl auf dem esxi-Host erzeugt:
    # $

    printVMs(allVMs)
    selectedVm = waitForUserInputToGetVMSelection(allVMs)

    isVmRunning = isSelectedVMRunning(selectedVm, onlineVMWs)
    if isVmRunning:
        print("VM currently UP! WorldId: " + selectedVm.worldId)
        # ToDo: stopVM()
    else:
        print("VM not running")


    #ToDo:  stopVM() registerVM() startVM()
    print("Parsing Done")
