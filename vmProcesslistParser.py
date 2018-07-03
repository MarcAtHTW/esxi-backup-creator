#!/usr/bin/python
"""
esxi-wmWare-Backup-Creator

@author Marc Sahib

"""

import re
import os
import argparse

from VM import VM
from OnlineVM import OnlineVM

"""
Führt Shell-Befehle auf dem ESXI-Host aus und stellt damit die zu parsenden Dateien zur Verfügung.
"""
def createDatasourceFiles():

    os.system("rm /backupScript/esxi-backup-creator/datasource/runningVMsList.txt")
    os.system("rm /backupScript/esxi-backup-creator/datasource/allVMsList.txt")
    os.system("esxcli vm process list >> /backupScript/esxi-backup-creator/datasource/runningVMsList.txt")
    os.system("vim-cmd vmsvc/getallvms >> /backupScript/esxi-backup-creator/datasource/allVMsList.txt")

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

def printBackups(Backups):
    cnt = 1
    for backup in Backups:
        print(str(cnt) + " : " + backup)
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

def waitForUserInputToGetBackupSelection(allBackups):
    print("Enter id to recover:")
    try:
        selectedBackup = int(input())
        if not 0 < selectedBackup <= len(allBackups):
            waitForUserInputToGetBackupSelection(allBackups)

        else:
            print("Backup \"" + allBackups[selectedBackup - 1] + "\" selected.")
            for backup in allBackups:
                if backup == allBackups[selectedBackup - 1]:
                    return backup
    except Exception as e:
        print("Enter a valid id from list." + e)
        waitForUserInputToGetVMSelection(allBackups)

def isSelectedVMRunning(selectedVM, onlineVMWs):
    isVMRunning = False

    for onlineVm in onlineVMWs:
        #Wenn die ausgewaehlte VM online ist, erhaelt sie die Infos des laufenden Prozesses.
        if selectedVM.name == onlineVm.name:
            selectedVM.configFile = onlineVm.configFile
            selectedVM.displayName = onlineVm.displayName
            selectedVM.processId = onlineVm.processId
            selectedVM.uuId = onlineVm.uuId
            selectedVM.vmxCartelId = onlineVm.vmxCartelId
            selectedVM.worldId = onlineVm.worldId
            isVMRunning = True

    return isVMRunning

"""
Fährt die VM herunter
"""
def shutDownVM(shutDownType, selectedVM):
    shutDownCommand = "esxcli vm process kill --type=" + shutDownType + " --world-id=" + selectedVM.worldId
    #print(shutDownCommand)
    os.system(shutDownCommand)

def startVM(selectedVM):
    startCommand = "vim-cmd vmsvc/power.on " + selectedVM.vmId
    os.system(startCommand)


def waitForUserInputShutdownConfirmation(selectedVM):
    isShutDownConfirmed = False;
    confirmation = input("Shutdown VM " + selectedVM.name + "?\ny/n:")
    if not re.match("^y(es)?$", confirmation):
        print("Shutdown not confirmed")
    else:
        print("Shutdown confirmed !")
        isShutDownConfirmed = True
    return isShutDownConfirmed

def backupVM(selectedVM):
    #[dataStore]
    dataStorePath = "/vmfs/volumes/5956536d-2a91849e-201b-1866da9841d4/" + selectedVM.name
    #QNAP-1
    backupStorePath = "/vmfs/volumes/5b2b744f-83de16a0-fe3b-1866da9841d4/Backup_VMs/" + selectedVM.name
    os.system("cp -r " + dataStorePath + " " + backupStorePath)

def getListOfBackups():
    return os.listdir('/vmfs/volumes/5b2b744f-83de16a0-fe3b-1866da9841d4/Backup_VMs/')


def recoverVM():
    #ToDo: Implement recoverVM()
    pass

def startBackupProcess():
    createDatasourceFiles()
    onlineVMWs = getOnlineVMs("/backupScript/esxi-backup-creator/datasource/runningVMsList.txt")
    allVMs = getAllVMs("/backupScript/esxi-backup-creator/datasource/allVMsList.txt")

    printVMs(allVMs)
    selectedVM = waitForUserInputToGetVMSelection(allVMs)

    isVmRunning = isSelectedVMRunning(selectedVM, onlineVMWs)
    if isVmRunning:
        print("VM currently UP! WorldId: " + selectedVM.worldId)
        isShutDownConfirmed = waitForUserInputShutdownConfirmation(selectedVM)
        if isShutDownConfirmed:
            shutDownVM("soft", selectedVM)

    backupVM(selectedVM)
    startVM(selectedVM)

def startRecoveryProcess():
    # ToDo: Recovery
    allBackups = getListOfBackups()
    printBackups(allBackups)
    selectedBackup = waitForUserInputToGetBackupSelection(allBackups)
    print(selectedBackup)


    # ToDo:  stopVM() registerVM() startVM()
    print("ToDo: stopVM(), copyVMToEsxi(), registerVM(), startVM()")
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b','--backup', action='store_true', help='Backup VM from ESXI to Backupstore')
    parser.add_argument('-r','--recover', action='store_true', help='Recover VM from Backupstore to ESXI')
    args = parser.parse_args()

    if args.backup == False and args.recover == False:
        print("Please use -h")

    if args.backup:
        startBackupProcess()
    elif args.recover:
        startRecoveryProcess()

    print("Parsing Done")