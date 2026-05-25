# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%bcond test 0
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

%global rocm_release 7.2
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global upstreamname amdsmi
# esmi_ib_library is not suitable for packaging
# https://github.com/amd/esmi_ib_library/issues/13
# This tag was chosen by the amdsmi project because 4.0+ introduced variables
# not found in the upstream kernel.
%global esmi_ver 4.2
%global pkg_library_version 26

Name:           amdsmi
Version:        %{rocm_version}
Release:        %autorelease
Summary:        AMD System Management Interface

License:        MIT AND (GPL-2.0-only WITH Linux-syscall-note) AND NSCA
# Main license is MIT
#
# This file is GPL-2.0:
# include/amd_smi/impl/amd_hsmp.h
# esmi_ib_library/include/asm/amd_hsmp.h
# Both carry: SPDX-License-Identifier: GPL-2.0 WITH Linux-syscall-note
#
# NSCA covers the bundled esmi_ib_library

Url:            https://github.com/ROCm/rocm-systems
VCS:            git:https://github.com/ROCm/rocm-systems.git
#!RemoteAsset:  sha256:23c31cd787d86ee35c82746fcde705eacc46517815110376f28417909ef46406
Source0:        %{url}/releases/download/rocm-%{version}/%{upstreamname}.tar.gz
#!RemoteAsset:  sha256:de19d222d09e2171f47f8bbd6608e5648bd547c82543379bb8fb5ed2e379e141
Source1:        https://github.com/amd/esmi_ib_library/archive/refs/tags/esmi_pkg_ver-%{esmi_ver}.tar.gz
BuildSystem:    cmake

# https://github.com/ROCm/amdsmi/pull/165
Patch0:         0001-Fix-compilation-with-libdrm-2.4.130.patch

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DBUILD_TESTS=%{build_test}
BuildOption(conf):  -DCMAKE_SKIP_INSTALL_RPATH=TRUE

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  linux-devel
BuildRequires:  ninja
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libdrm_amdgpu)
BuildRequires:  python3-devel
%if %{with test}
BuildRequires:  cmake(GTest)
%endif

Requires:       python3dist(pyyaml)

# University of Illinois/NCSA Open Source License
Provides:       bundled(esmi_ib_library) = %{esmi_ver}

%description
The AMD System Management Interface Library, or AMD SMI library, is a C
library for Linux that provides a user space interface for applications
to monitor and control AMD devices.

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
%{summary}

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%autosetup -p1 -n %{upstreamname}

tar xf %{SOURCE1}
mv esmi_ib_library-* esmi_ib_library
# So we can pick up this license
mv esmi_ib_library/License.txt esmi_ib_library_License.txt
# The esmi version check uses git tags, but we use tar's without git files.
# Just inject in the tag that we've pulled into the version check:
sed -i 's/NOT latest_esmi_tag/NOT "esmi_pkg_ver-%{esmi_ver}"/' CMakeLists.txt

# W: spurious-executable-perm /usr/share/doc/amdsmi/README.md
chmod a-x README.md

# /usr/libexec/amdsmi_cli/BDF.py:126: SyntaxWarning: invalid escape sequence '\.'
sed -i -e 's@bdf_regex = "@bdf_regex = r"@' amdsmi_cli/BDF.py

# Fix script shebang
sed -i -e 's@env python3@python3@' amdsmi_cli/*.py

%if %{with test}
# Install local gtests in same dir as tests
sed -i -e 's@${CPACK_PACKAGING_INSTALL_PREFIX}/lib@${SHARE_INSTALL_PREFIX}/tests@' tests/amd_smi_test/CMakeLists.txt
%endif

# fix cstdint include
# https://github.com/ROCm/amdsmi/issues/123
sed -i '/#include <unordered_set.*/a#include <cstdint>' rocm_smi/include/rocm_smi/rocm_smi_common.h

%if %{with test}
# fix iomanip include
# https://github.com/ROCm/amdsmi/issues/124
sed -i '/#include <string.*/a#include <iomanip>' tests/amd_smi_test/test_common.h
%endif

%install -a
mkdir -p %{buildroot}%{_libdir}/python%{python3_version}/site-packages
if [ -d %{buildroot}%{_datadir}/amd_smi/amdsmi ]; then
    mv %{buildroot}%{_datadir}/amd_smi/amdsmi %{buildroot}%{_libdir}/python%{python3_version}/site-packages
    mv %{buildroot}%{_datadir}/amd_smi/pyproject.toml %{buildroot}%{_libdir}/python%{python3_version}/site-packages/amdsmi/
else
    mv %{buildroot}%{_datadir}/amdsmi %{buildroot}%{_libdir}/python%{python3_version}/site-packages
    mv %{buildroot}%{_datadir}/pyproject.toml %{buildroot}%{_libdir}/python%{python3_version}/site-packages/amdsmi/
fi

# W: unstripped-binary-or-object .../amdsmi/libamd_smi.so
# Does an explicit open, so can not just rm it; strip it instead
strip %{buildroot}%{_libdir}/python%{python3_version}/site-packages/amdsmi/*.so
# E: non-executable-script .../amdsmi_cli/amdsmi_cli_exceptions.py 644 /usr/bin/env python3
chmod a+x %{buildroot}%{_libexecdir}/amdsmi_cli/amdsmi_*.py

rm -rf %{buildroot}%{_datadir}/example
rm -rf %{buildroot}%{_datadir}/amd_smi/example
rm -f %{buildroot}%{_datadir}/doc/amd_smi-asan/LICENSE.txt
rm -f %{buildroot}%{_datadir}/doc/amd-smi-lib/LICENSE.txt
rm -f %{buildroot}%{_datadir}/doc/amd-smi-lib/README.md
rm -rf %{buildroot}%{_datadir}/doc/amd-smi-lib/copyright
rm -f %{buildroot}%{_datadir}/_version.py
rm -f %{buildroot}%{_datadir}/amd_smi/_version.py
rm -f %{buildroot}%{_datadir}/setup.py
rm -f %{buildroot}%{_datadir}/amd_smi/setup.py

if [ -e %{buildroot}%{_datadir}/amd_smi/tests ]; then
    mkdir -p %{buildroot}%{_datadir}/amdsmi
    mv %{buildroot}%{_datadir}/amd_smi/tests %{buildroot}%{_datadir}/amdsmi/
fi

%files
%doc README.md
%license LICENSE
%license esmi_ib_library_License.txt
%{_libdir}/libamd_smi.so.%{pkg_library_version}{,.*}
%{_libdir}/libgoamdsmi_shim64.so.1{,.*}
%{_bindir}/amd-smi
%{_libexecdir}/amdsmi_cli
%{_libdir}/python%{python3_version}/site-packages/amdsmi

%files devel
%{_includedir}/amd_smi/
%{_includedir}/*.h
%{_libdir}/libamd_smi.so
%{_libdir}/cmake/amd_smi/
%{_libdir}/libgoamdsmi_shim64.so

%if %{with test}
%files test
%{_datadir}/amdsmi/
%endif

%changelog
%autochangelog

