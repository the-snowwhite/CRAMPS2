import qbs

MachinekitApplication {
    name: "MibRap-X"
    halFiles: ["MibRapX.hal",
               "velocity-extruding.hal"]
    configFiles: ["MibRapX.ini"]
    bbioFiles: ["paralell_cape3.bbio"]
    otherFiles: ["tool.tbl", "subroutines"]
    compFiles: ["led_dim.comp", "thermistor_check.comp"]
    linuxcncIni: "MibRapX.ini"
    //display: "thinkpad.local:0.0"
}
