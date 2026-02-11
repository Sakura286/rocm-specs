# SPDX-FileCopyrightText: (C) 2025 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2025 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global upstreamname rocprofiler-register
%global rocm_release 7.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}

Name:           rocprofiler-register
Version:        %{rocm_version}
Release:        %autorelease
Summary:        A rocprofiler helper library
License:        MIT AND BSD-3-Clause
Url:            https://github.com/ROCm/%{upstreamname}
#!RemoteAsset
Source0:        %{url}/archive/rocm-%{rocm_version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -DROCPROFILER_REGISTER_BUILD_TESTS=%{?with_test:ON}%{!?with_test:OFF}
BuildOption(conf):  -DROCPROFILER_REGISTER_BUILD_FMT=OFF
BuildOption(conf):  -DROCPROFILER_REGISTER_BUILD_GLOG=OFF

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  glog-devel
BuildRequires:  pkgconfig(fmt)
BuildRequires:  pkgconfig(gflags)

%description
The rocprofiler-register library is a helper library that coordinates
the modification of the intercept API table(s) of the HSA/HIP/ROCTx
runtime libraries by the ROCprofiler (v2) library. The purpose of this
library is to provide a consistent and automated mechanism of enabling
performance analysis in the ROCm runtimes which does not rely on
environment variables or unique methods for each runtime library.

When a runtime is initialized (either explicitly and lazily) and the
intercept API table is constructed, it passes this API table to
rocprofiler-register. Rocprofiler-register scans the symbols in the
address space and if it detects there is at least one visible symbol
named rocprofiler_configure (which is a function provided by tools),
it passes the intercept API table to the rocprofiler library (dlopening
the rocprofiler library if it is not already loaded). The rocprofiler
library then does an extensive scan for all the instances of the
rocprofiler_configure symbols and invokes each of them. The
rocprofiler_configure function (again, provided by a tool) returns
effectively tells rocprofiler which behaviors it wants to be notified
about, features it wants to use (e.g. API tracing, kernel dispatch
timing), etc.

%package        devel
Summary:        The development package for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{summary}

%prep -a
# When using the system fmt, need to change this link
sed -i 's@fmt::fmt glog::glog@fmt glog@' source/lib/rocprofiler-register/CMakeLists.txt

# Do not hardcode install lib
sed -i 's@set(CMAKE_INSTALL_LIBDIR@#set(CMAKE_INSTALL_LIBDIR@' CMakeLists.txt

%install -a
# Do not install the test source etc
rm -rf %{buildroot}%{_prefix}/share/rocprofiler-register
rm -rf %{buildroot}%{_prefix}/share/modulefiles
rm -rf %{buildroot}%{_prefix}/share/doc/rocprofiler-register/LICENSE.md

%check
%{?with check:%ctest}

%files
%license LICENSE.md
%{_libdir}/librocprofiler-register.so.0{,.*}

%files devel
%doc README.md
%{_includedir}/rocprofiler-register/
%{_libdir}/librocprofiler-register.so
%{_libdir}/cmake/rocprofiler-register/

%changelog
%{?autochangelog}
