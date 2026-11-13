# SPDX-FileCopyrightText: (C) 2025 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2025 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global upstreamname rocm_bandwidth_test
%global rocm_release 7.2
%global rocm_patch 4
%global rocm_version %{rocm_release}.%{rocm_patch}

# GPU HW is required to run %check, and needs to run locally
%bcond check 0

Name:           rocm-bandwidth-test
Version:        %{rocm_version}
Release:        %autorelease
Summary:        Bandwidth test for ROCm
License:        MIT
URL:            https://github.com/ROCm/rocm_bandwidth_test
#!RemoteAsset:  sha256:abba532eeb43f0740ed9bbacc39ff738a55acae0f01ba5d75a899e313ddc35ea
Source0:        %{url}/archive/06dd9df114855ed2dc38cd731ad214066a62d6da/rocm_bandwidth_test-06dd9df114855ed2dc38cd731ad214066a62d6da.tar.gz
Source1:        distro-install.cmake
BuildSystem:    cmake

# No therock-10.1 release exists for this standalone tool; use latest tagged source.
BuildOption(prep):  -n rocm_bandwidth_test-06dd9df114855ed2dc38cd731ad214066a62d6da

BuildOption(conf):  -DAMD_APP_ROCM_BUILD_AUTO_DETECT=OFF
BuildOption(conf):  -DAMD_APP_ROCM_BUILD_PACKAGE=OFF
BuildOption(conf):  -DAMD_APP_SUBMODULES_TRY_CHECKOUT=OFF
BuildOption(conf):  -DAMD_APP_TREAT_WARNINGS_AS_ERRORS=OFF
BuildOption(conf):  -DAMD_WORK_BENCH_INCLUDE_PLUGINS='builtin;tb'
BuildOption(conf):  -DUSE_LOCAL_FMT_LIB=ON
BuildOption(conf):  -DUSE_LOCAL_NLOHMANN_JSON=ON
BuildOption(conf):  -DUSE_LOCAL_SPDLOG=ON
BuildOption(conf):  -DUSE_LOCAL_BOOST=ON
BuildOption(conf):  -DUSE_LOCAL_BOOST_STACKTRACE=ON
BuildOption(conf):  -DUSE_LOCAL_CLI11=ON
BuildOption(conf):  -DUSE_LOCAL_CATCH2=ON
BuildOption(conf):  -DROCM_PATH=%{_prefix}
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++
BuildOption(conf):  -DCMAKE_CXX_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
BuildOption(conf):  -DCMAKE_SKIP_RPATH=ON

BuildRequires:  make
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  cmake
BuildRequires:  boost-devel
BuildRequires:  cmake(Catch2)
BuildRequires:  cmake(CLI11)
BuildRequires:  cmake(fmt)
BuildRequires:  cmake(nlohmann_json)
BuildRequires:  cmake(spdlog)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(numa)
BuildRequires:  clang(major) = 24
BuildRequires:  chrpath
BuildRequires:  hipcc
BuildRequires:  rocm-cmake >= 10.1.0
BuildRequires:  rocm-hip-devel >= 10.1.0
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocr-runtime-devel >= 10.1.0

%description
ROCm Bandwidth Test is designed to capture the performance
characteristics of buffer copying and kernel read and write
operations. The benchmark help screen shows various options
for initiating copy, read, and write operations. In
addition to this, you can also query the system topology in
terms of memory pools and their agents.

%prep -a
# Select the distribution CMake package names and exported CLI11 target.
sed -i -e 's/set(BOOST_PACKAGE_NAME "boost")/set(BOOST_PACKAGE_NAME "Boost")/' \
    -e 's/set(CATCH2_PACKAGE_NAME "catch2")/set(CATCH2_PACKAGE_NAME "Catch2")/' \
    cmake/build_utils.cmake
sed -i 's/find_package(${FMT_PACKAGE_NAME} REQUIRED ${FMT_PKG_MINIMUM_REQUIRED_VERSION})/find_package(${FMT_PACKAGE_NAME} ${FMT_PKG_MINIMUM_REQUIRED_VERSION} REQUIRED)/' cmake/build_utils.cmake
sed -i 's/find_package(${SPDLOG_PACKAGE_NAME} REQUIRED ${SPDLOG_PKG_MINIMUM_REQUIRED_VERSION})/find_package(${SPDLOG_PACKAGE_NAME} ${SPDLOG_PKG_MINIMUM_REQUIRED_VERSION} REQUIRED)/' cmake/build_utils.cmake
sed -i 's/find_package(${CATCH2_PACKAGE_NAME} REQUIRED ${CATCH2_PKG_MINIMUM_REQUIRED_VERSION})/find_package(${CATCH2_PACKAGE_NAME} ${CATCH2_PKG_MINIMUM_REQUIRED_VERSION} REQUIRED)/' cmake/build_utils.cmake
sed -i -e 's/find_package(CLI11 CONFIG QUIT)/find_package(CLI11 CONFIG REQUIRED)\n    set(CLI11_LIBRARIES CLI11::CLI11)/' \
    main/cmdline/CMakeLists.txt
# Pass the configured GPU set to the separately configured TransferBench engine.
sed -i '/-DCMAKE_BUILD_TYPE=/a\                                -DGPU_TARGETS=%{rocm_gpu_list_default} \\' \
    plugins/tb/transferbench/build_libamd_tb.sh
# Use conventional install rules rather than upstream's /opt staging packager.
# Keep the library ABI version while RPM owns installation and packaging.
sed -i 's/^setup_distribution_package()$/set_target_properties(${AMD_TARGET_LIBNAME} PROPERTIES SOVERSION ${AMD_TARGET_VERSION})/' CMakeLists.txt
cat %{SOURCE1} >> CMakeLists.txt

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH
export ROCM_PATH=%{_prefix}

%build -p
export ROCM_PATH=%{_prefix}
export HIPCC_COMPILE_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu --rocm-device-lib-path=%{_libdir}/llvm24/lib/clang/24/amdgcn/bitcode"
export HIPCC_LINK_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu --rocm-device-lib-path=%{_libdir}/llvm24/lib/clang/24/amdgcn/bitcode"

%install -a
chrpath --delete %{buildroot}%{_libdir}/libamd_tb.so*

%check
%if %{with check}
LD_LIBRARY_PATH="$PWD/lib:$PWD/plugins/tb/lib" \
    %{_vpath_builddir}/rocm_bandwidth_test run tb
%endif

%files
%doc README.md CHANGELOG.md
%license LICENSE.md
%{_bindir}/rocm-bandwidth-test
%{_bindir}/rocm_bandwidth_test
%{_libdir}/libamd_work_bench.so*
%{_libdir}/libamd_tb.so*
%{_libdir}/rocm_bandwidth_test/

%changelog
%autochangelog
