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
# License mismatch
# https://github.com/ROCm/rocm_bandwidth_test/issues/127
License:        NCSA AND MIT
URL:            https://github.com/ROCm/rocm_bandwidth_test
#!RemoteAsset:  sha256:eb3256351c00123d4536e93dd1500f5edd6fa46e5acd777c6cce8f9db894ccc0
Source0:        %{url}/archive/rocm-%{version}.tar.gz
# From base_test.cpp
Source1:        LICENSE.NCSA.txt
# Upstream's USE_LOCAL_* (system-library) cmake paths are undertested: the
# fmt/spdlog/Catch2 find_package() put the version after REQUIRED (so it is parsed
# as a bogus component and FOUND is set FALSE), Boost/Catch2 are looked up with a
# lowercase name that misses their *Config.cmake, and the CLI11 system branch never
# sets CLI11_LIBRARIES. The patch also turns the "no distribution package type"
# FATAL into a warning so we can skip upstream's CPack/staging install and package
# the build artifacts directly with rpmbuild (see %install).
Patch0:         0001-use-system-libs-via-find_package.patch
BuildSystem:    cmake

BuildRequires:  clang22
BuildRequires:  git
BuildRequires:  make
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  pkgconfig(fmt)
BuildRequires:  cmake(spdlog)
BuildRequires:  cmake(nlohmann_json)
BuildRequires:  cmake(CLI11)
BuildRequires:  cmake(Catch2)
BuildRequires:  boost-devel
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocr-runtime-devel >= %{rocm_release}.0
BuildRequires:  cmake(hip)
BuildRequires:  numactl-devel
BuildRequires:  pkgconfig(libcurl)

# Use the distro's system libraries instead of the bundled (empty in the release
# tarball) git submodules. Catch2 is resolved unconditionally even with tests off,
# so it must use the system lib too; jthread is skipped (C++20 std::jthread).
BuildOption(conf):  -DUSE_LOCAL_FMT_LIB=ON
BuildOption(conf):  -DUSE_LOCAL_SPDLOG=ON
BuildOption(conf):  -DUSE_LOCAL_NLOHMANN_JSON=ON
BuildOption(conf):  -DUSE_LOCAL_CLI11=ON
BuildOption(conf):  -DUSE_LOCAL_CATCH2=ON
BuildOption(conf):  -DUSE_LOCAL_BOOST=ON

# Skip the TransferBench (tb) plugin: it is a nested ExternalProject that compiles
# HIP device code with hipcc for every GPU arch, which needs a working GPU toolchain
# (rocm_agent_enumerator) in the build root and cannot be verified without a GPU.
# The core bandwidth-test binary and the builtin/amd-hello plugins do not need it.
BuildOption(conf):  -DAMD_WORK_BENCH_EXCLUDE_PLUGINS=tb
# The core libamd_work_bench trips -Werror=unused-parameter under the default GNU
# toolchain; upstream promotes warnings to errors by default.
BuildOption(conf):  -DAMD_APP_TREAT_WARNINGS_AS_ERRORS=OFF

%description
ROCm Bandwidth Test is designed to capture the performance
characteristics of buffer copying and kernel read and write
operations. The benchmark help screen shows various options
for initiating copy, read, and write operations. In
addition to this, you can also query the system topology in
terms of memory pools and their agents.

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH

%prep -a
# Remove execute permissions on docs
# https://github.com/ROCm/rocm_bandwidth_test/issues/128
chmod a-x LICENSE.md
chmod a-x README.md
cp %{SOURCE1} .

%install -a
# Upstream's CPack/staging "distribution package" install is bypassed (see Patch0);
# install the artifacts by hand. The build emits the ELF plus a 'rocm-bandwidth-test'
# symlink in the vpath build dir, the plugins as *.amdplug, and the internal
# libamd_work_bench shared library.
install -Dm0755 %{_vpath_builddir}/%{upstreamname} %{buildroot}%{_bindir}/%{upstreamname}
ln -sf %{upstreamname} %{buildroot}%{_bindir}/%{name}

# The internal shared lib goes in the standard libdir so the dynamic linker (and the
# dlopen'd plugins) resolve it by default, without RPATH.
install -dm0755 %{buildroot}%{_libdir}
find . -name 'libamd_work_bench.so*' -exec cp -a -t %{buildroot}%{_libdir}/ {} +

# Plugins are dlopen'd from the path baked into the binary at build time
# (SYSTEM_DEFAULT_PLUGIN_INSTALL_PATH = %{_libdir}/%{upstreamname}, scanned directly).
install -dm0755 %{buildroot}%{_libdir}/%{upstreamname}
install -m0755 %{_vpath_builddir}/plugins/*.amdplug %{buildroot}%{_libdir}/%{upstreamname}/

%check
%if %{with check}
%{_vpath_builddir}/rocm-bandwidth-test
# On a gfx1201, the start should look something like
#          RocmBandwidthTest Version: 2.6.0
#
#          Launch Command is: redhat-linux-build/rocm-bandwidth-test (rocm_bandwidth -a + rocm_bandwidth -A)
#
#
#          Device: 0,  Intel(R) Core(TM) i5-10400 CPU @ 2.90GHz
#          Device: 1,  AMD Radeon Graphics,  GPU-7b2a57bc7a036a5f,  03:0.0
# ...
%endif

%files
%doc README.md
%license LICENSE.md LICENSE.NCSA.txt
%{_bindir}/%{upstreamname}
%{_bindir}/%{name}
%{_libdir}/libamd_work_bench.so*
%{_libdir}/%{upstreamname}/

%changelog
%autochangelog
