tdaq_package()

find_package(Qt5 QUIET REQUIRED COMPONENTS Widgets Gui Core HINTS ${QT5_ROOT})

tdaq_add_library(TileCIS              src/DetectorObject.cxx
                                      src/TileBuilder.cxx         
                                      src/TileCommand.cxx         
                                      src/TileDetector.cxx        
                                      src/TileTarget.cxx          
                                      src/TileState.cxx           
                                      src/TileDrawerModuleCIS.cxx 
                                      src/pipeline.cxx
                                LINK_LIBRARIES  TileVMEboards Tiledal tdaq::RCDLtp tdaq::cmdline)

tdaq_add_executable(tilecis     src/tilecis.cxx
                                LINK_LIBRARIES TileCIS readline history termcap tdaq::cmdline stdc++fs)

macro(tdaq_ui_output_name output input)
  set(${output} ${CMAKE_CURRENT_BINARY_DIR}/${input}_ui.h)
endmacro()

qt5_wrap_ui(qt_uic src/qt/TileCISPanel.ui)


qt5_wrap_cpp(qt_moc TileCIS/editscript.h)

tdaq_add_executable(TileCISPanel src/main.cpp
                                 src/editscript.cpp
                                 ${qt_uic}
                                 ${qt_moc}
                                LINK_LIBRARIES TileCIS Qt5::Widgets Qt5::Gui Qt5::Core
                                OPTIONS -Wno-deprecated)
