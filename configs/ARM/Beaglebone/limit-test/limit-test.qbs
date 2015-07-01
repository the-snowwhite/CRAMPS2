import qbs

MachinekitApplication {
    name: "limit-test"
    halFiles: ["limit-test.hal",
               "velocity-extruding.hal"]
    configFiles: ["limit-test.ini"]
    bbioFiles: ["limit-test_cape.bbio"]
    otherFiles: ["tool.tbl", "subroutines"]
    compFiles: ["thermistor_check.comp"]
    linuxcncIni: "limit-test.ini"
    //display: "thinkpad.local:0.0"
}
