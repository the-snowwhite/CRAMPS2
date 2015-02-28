import qbs

MachinekitApplication {
    name: "Prusa-i3"
    halFiles: ["CRAMPS2.hal",
               "velocity-extruding.hal"]
    configFiles: ["CRAMPS2.ini"]
    bbioFiles: ["cramps2_cape.bbio"]
    otherFiles: ["tool.tbl", "subroutines"]
    compFiles: ["thermistor_check.comp"]
    linuxcncIni: "CRAMPS2.ini"
    //display: "thinkpad.local:0.0"
}
