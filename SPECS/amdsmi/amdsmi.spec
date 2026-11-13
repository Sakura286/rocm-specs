# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# amdSMI's gtest client (amdsmitst) needs GPU/driver to run
%bcond run_test 0

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}

%global esmi_commit d494a3194ceb4cc4dbb2debf9fcbe8773c6d3bef
%global pkg_library_version 27

Name:           amdsmi
Version:        %{rocm_version}
Release:        %autorelease
Summary:        AMD System Management Interface
# Main license is MIT
#
# include/amd_smi/impl/amd_hsmp.h
# esmi_ib_library/include/asm/amd_hsmp.h
# Both carry: SPDX-License-Identifier: GPL-2.0 WITH Linux-syscall-note
#
# Bundled esmi_ib_library is NCSA
License:        MIT AND (GPL-2.0-only WITH Linux-syscall-note) AND NCSA
URL:            https://github.com/ROCm/amdsmi
# ROCm 10.1.0 source release uses the therock-10.1 tag.
#!RemoteAsset:  sha256:550ecc98dd7e73f7b70fb0c0eeb66fa3bc9fba19644622e76dfb67f8529e1a70
Source0:        https://github.com/ROCm/rocm-systems/releases/download/therock-10.1/amdsmi.tar.gz
#!RemoteAsset:  sha256:8f9cf10922276ca35872ca0bc27e29e717a472ba704a575c5497622b62049e75
Source1:        https://github.com/amd/esmi_ib_library/archive/%{esmi_commit}/esmi_ib_library-%{esmi_commit}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DAMDSMI_SYSTEM_PYTHON_SITELIB=%{python3_sitearch}
BuildOption(conf):  -DBUILD_TESTS=ON
BuildOption(conf):  -DCMAKE_SKIP_INSTALL_RPATH=TRUE
%ifnarch x86_64
BuildOption(conf):  -DENABLE_ESMI_LIB=OFF
%endif

BuildRequires:  cmake
BuildRequires:  cmake(GTest)
BuildRequires:  ninja
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libnl-3.0)
BuildRequires:  pkgconfig(libnl-genl-3.0)
BuildRequires:  pkgconfig(libmnl)
BuildRequires:  pkgconfig(libdrm_amdgpu)
BuildRequires:  pkgconfig(python3)

Requires:       python3dist(pyyaml)

%patchlist
# -DENABLE_ESMI_LIB=OFF is not enough
# Goamdshim calls CPU/ESMI-only APIs; skip building it when ESMI is off
2001-Disable-goamdsmi_shim-when-ESMI-is-off.patch

%global _description %{expand:
The AMD System Management Interface Library, or AMD SMI library, is a C
library for Linux that provides a user space interface for applications
to monitor and control AMD devices.
}

%description
%{_description}

%package        devel
Summary:        Libraries and headers for %{name}
Provides:       %{name}-static = %{version}-%{release}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{_description}

%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}

%prep
%autosetup -p1 -n amdsmi

# ESMI - EPYC System Management Interface
# esmi_ib_library uses x86-only cpuid.h; guard it for non-x86 builds
%ifarch x86_64
tar xf %{SOURCE1}
mv esmi_ib_library-* esmi_ib_library
mv esmi_ib_library/License.txt esmi_ib_library_License.txt
%endif

# Fix script shebang
sed -i -e 's@env python3@python3@' amdsmi_cli/*.py

%install -a
# Upstream installs the module directly into the configured Python sitearch.
# Remove the duplicate relocatable-tree copy; use the system SONAME loader.
rm -rf %{buildroot}%{_datadir}/amd_smi
# Wheel generation helper is not used by the system package.
rm -f %{buildroot}%{_datadir}/tools/disable_system_fallback.py

# E: non-executable-script .../amdsmi_cli/amdsmi_cli_exceptions.py 644 /usr/bin/env python3
chmod a+x %{buildroot}%{_libexecdir}/amdsmi_cli/amdsmi_*.py

rm -f %{buildroot}%{_datadir}/_version.py
rm -f %{buildroot}%{_datadir}/amd_smi/_version.py
rm -rvf %{buildroot}%{_datadir}/amd_smi/example
rm -f %{buildroot}%{_datadir}/amd_smi/setup.py
rm -rvf %{buildroot}%{_datadir}/example
rm -f %{buildroot}%{_datadir}/setup.py
rm -f %{buildroot}%{_docdir}/amd-smi-lib/LICENSE.txt
rm -f %{buildroot}%{_docdir}/amd-smi-lib/README.md
rm -rvf %{buildroot}%{_docdir}/amd-smi-lib/copyright
rm -f %{buildroot}%{_docdir}/amd_smi-asan/LICENSE.txt

if [ -e %{buildroot}%{_datadir}/tests ]; then
    mkdir -p %{buildroot}%{_datadir}/amdsmi
    mv %{buildroot}%{_datadir}/tests %{buildroot}%{_datadir}/amdsmi/tests
fi

# amdsmitst needs GPU/driver access to run
%if %{without run_test}
%check
%endif

%files
%doc README.md
%license LICENSE
%{_bindir}/amd-smi
%{_libdir}/libamd_smi.so.%{pkg_library_version}{,.*}
%{_libexecdir}/amdsmi_cli
%{python3_sitearch}/amdsmi
%ifarch x86_64
%license esmi_ib_library_License.txt
%{_libdir}/libgoamdsmi_shim64.so.1{,.*}
%endif

%files devel
%{_includedir}/amd_smi/
%{_libdir}/cmake/amd_smi/
%{_libdir}/libamd_smi.so
%{_libdir}/libamd_smi_static.a
%{_libdir}/libamdsminic.a
%{_includedir}/rocm_smi/rocm_smi_logger.h
%ifarch x86_64
%{_includedir}/*.h
%{_includedir}/e_smi/
%{_libdir}/libgoamdsmi_shim64.so
%endif

%files test
%{_datadir}/amdsmi/

%changelog
%autochangelog
