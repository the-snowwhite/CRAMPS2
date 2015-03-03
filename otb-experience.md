## BBB CRAMPS Machineface 3D Printer Out-Of-The-Box Experience ##
(Quickstart guide for 3D FDM printing with Machinekit on Beaglebone Black with Cramps cape)

this setup uses the mkwrapper based QTQuickVCP UI by Alexander Rössler

---------


1 Source: http://blog.machinekit.io/2015_01_01_archive.html  

Download bone-debian-7.8-machinekit-armhf-2015-xx-xx-4gb.img.xz from:
 http://elinux.org/Beagleboard:BeagleBoneBlack_Debian#BBW.2FBBB_.28All_Revs.29_Machinekit
 
current newest image is: bone-debian-7.8-machinekit-armhf-2015-02-15-4gb.img.xz
    
    wget https://rcn-ee.net/rootfs/bb.org/testing/2015-02-15/machinekit/bone-debian-7.8-machinekit-armhf-2015-02-15-4gb.img.xz

	md5sum: 79ca23e60fc31602ee974cf585855ea1
2.a verify image  (source: http://blog.machinekit.io/p/machinekit_16.html)
    
    md5sum bone-debian-7.8-machinekit-armhf-2015-02-15-4gb.img.xz

2.b copy image to sd card (source: http://blog.machinekit.io/p/machinekit_16.html):
[note 1: replace X in sdX with you sdcard mount point]
[note 2: you can also use windiskimager to copy to sdcard if you only have an Windows PC available]

    xzcat bone-debian-7.8-machinekit-armhf-2015-02-15-4gb.img.xz | dd bs=1M of=/dev/sdX
    or
    sudo bash -c 'xzcat bone-debian-7.8-machinekit-armhf-2015-02-15-4gb.img.xz | dd bs=1M of=/dev/sdX'

3 attach CRAMPS to BBB and insert sd card into BBB (you can later edit uenv.txt to flash the sdcard contents into emmc flash)

4.a connect LAN cable (+ evt. monitor, mouse and keyboard to BBB)
4.b. connect +5V and ground to cramps (power on and device boots from sd-card)
[note: power off button only not working on  first boot]

5 either connect to your BBB via ssh:
	
	ssh -X machinekit@beaglebone.local 
(pw: machinekit)

or just open a console on you BBB if you have keyboard and display attached to your BBB 

6 update packages:
	
	machinekit@beaglebone:~$ sudo apt-get update
    machinekit@beaglebone:~$ sudo apt-get upgrade

if --> The following packages have been kept back:
	machinekit machinekit-xenomai
 
	 machinekit@beaglebone:~$ sudo apt-get dist-upgrade

7 	you need machinekit-dev package to be able to compile the custom components on first run
otherwise you will get the comp not found error message:

	machinekit@beaglebone:~$ sudo apt-get install machinekit-dev

8 do a test:

    machinekit@beaglebone:~$ halrun
    msgd:0 stopped
    rtapi:0 stopped
    halcmd: loadusr halmeter
    halcmd: exit
    
   if --> halcmd: Gtk-Message: Failed to load module "canberra-gtk-module"
   
	   machinekit@beaglebone:~$ sudo apt-get install libcanberra-gtk-module
and retry step 8 [note: you may have to log out and in again and halrun may give some error messages
just rerun it. You do not have to reboot at this point]
9  install machineface and/or  cetus in the root of your home folder 
    (source: https://github.com/strahlex/QtQuickVcp/wiki/Testing-mkwrapper) 
    
	machinekit@beaglebone:~$ cd ~/    
	machinekit@beaglebone:~$ git clone https://github.com/strahlex/Machineface.git
	machinekit@beaglebone:~$ git clone https://github.com/strahlex/Cetus.git
	
10 To enable remote communication you have to edit the REMOTE variable in the ini-file:
	
	machinekit@beaglebone:~$ sudo nano /etc/linuxcnc/machinekit.ini
	change REMOTE=0 to REMOTE=1;
	save (ctrl-x .. y .. enter)

11.a Copy CRAMPS2 configurations into the root of home

	machinekit@beaglebone:~$ cd ~/
	machinekit@beaglebone:~$ git clone https://github.com/the-snowwhite/CRAMPS2.git 

11.b modify CRAMPS_QVCP.ini

	machinekit@beaglebone:~$ leafpad ~/CRAMPS2/configs/ARM/Beaglebone/CRAMPS_QVCP.ini
	
	machine limits, home, home offset
	scale
	thermistor type
	 
11.c

	make script file executable:
	machinekit@beaglebone:~$ chmod +x ~/CRAMPS2/configs/ARM/Beaglebone/run.py
	 
12.a before you reboot you might would like to change the network hostname to something other than the default beaglebone, also you may want to connect it to your network workgroup/localdomain 

	machinekit@beaglebone:~$ sudo nano /etc/hostname
edit beaglebone to what you prefer (ex: BBB)

	(ctrl-x .. y .. enter)

	machinekit@beaglebone:~$ sudo nano /etc/hosts
edit line 2-->
replace beaglebone with your new hostname
replace localdomain with your workgroup/localdomain
ie:
	
	127.0.1.1       beaglebone.localdomain  beaglebone
-->
	
	127.0.1.1       BBB.holotronic  BBB     
	 	
12 reboot 
	
	machinekit@beaglebone:~$ sudo reboot -n

 
13.a Before running your config you have to create an empty folder named nc_files in root of home

	ssh -X machinekit@bbb
	machinekit@BBB:~$ mkdir nc_files

13.b then run the startup script:

	machinekit@BBB:~$ ~/CRAMPS2/configs/ARM/Beaglebone/CRAMPS-QVCP/run.py
 
 Your first run should look somthing like this:

	machinekit@BBB:~$ ~/CRAMPS2/configs/ARM/Beaglebone/CRAMPS-QVCP/run.py
	loading cramps2_cape.bbio... Loading cape-universal overlay
	Loading cape-bone-iio overlay
	done
	installing thermistor_check.comp... Compiling realtime thermistor_check.c
	Linking thermistor_check.so
	cp thermistor_check.so /usr/lib/linuxcnc/xenomai/
	done
	starting configserver... done
	starting linuxcnc... done
	LINUXCNC - 2.7.0~pre0
	Machine configuration directory is '/home/machinekit/CRAMPS2/configs/ARM/Beaglebone/CRAMPS-QVCP'
	Machine configuration file is 'CRAMPS_QVCP.ini'
	Starting LinuxCNC...
	io started
	halcmd loadusr io started
	task pid=3121
	emcTaskInit: using builtin interpreter
	/usr/lib/python2.7/dist-packages/pyftpdlib/authorizers.py:262: RuntimeWarning: write permissions assigned to anonymous user.
	  RuntimeWarning)

You shutdown the server via ctrl-c

14 The Machine Client is available here:
https://github.com/strahlex/QtQuickVcp/releases
source:
https://github.com/strahlex/QtQuickVcp/wiki/Testing-mkwrapper

I had to compile Machinkit-Client 0.9 v3(QtQuickVcp/applications/AppDiscover/AppDiscover.pro)
to get past the:
			
		  QML Error:
	Loading QML file failed
	
message.

15 Slic3r is the recomended slicer program.
my current settings are:

Printer Settings->General:
G-code flavor
	
	Mach3/LinuxCNC

Printer Settings->Custom G-code:
Start G-code:

	G90
	G28 ; home all axes
	G92 A0 ; zero extruder
	G1 Z5 F5000 ; lift nozzle
End G-code:

	G1 Z40 F5000 ; lift nozzle
	M104 P0 ; turn off temperature
	M140 P0 ; turn off temperature of heatbed
	G90 ; ablolute coordinates
	G53 X0 Y0 ; home X,Y axis
	M2 ; End the program
	
Print Settings->Output options
Output file

	Output filename format: [input_filename_base].ngc