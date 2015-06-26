import qbs

MachinekitApplication {
    name: "Prusa-i3"
    halFiles: ["Prusa-i3.hal",
               "velocity-extruding.hal"]
    configFiles: ["Prusa-i3.ini"]
    bbioFiles: ["Prusa-i3_cape.bbio"]
    otherFiles: ["tool.tbl", "subroutines"]
    compFiles: ["thermistor_check.comp"]
    linuxcncIni: "Prusa-i3.ini"
    //display: "thinkpad.local:0.0"
}
