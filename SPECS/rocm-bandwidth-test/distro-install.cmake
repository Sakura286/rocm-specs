# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-License-Identifier: MIT
include(GNUInstallDirs)
install(TARGETS awb_main RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES "${CMAKE_BINARY_DIR}/rocm-bandwidth-test"
        DESTINATION ${CMAKE_INSTALL_BINDIR})
install(TARGETS libamd_work_bench LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(TARGETS builtin transferbench
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/rocm_bandwidth_test/plugins)
install(DIRECTORY "${CMAKE_SOURCE_DIR}/plugins/tb/lib/"
        DESTINATION ${CMAKE_INSTALL_LIBDIR}
        FILES_MATCHING PATTERN "libamd_tb.so*")
