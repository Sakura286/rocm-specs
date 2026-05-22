# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# hipRAND needs a GPU to run tests, but we could still
# keep the test cases for packagers who have a GPU, so make it optional.
%bcond test 0
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

# rocm stack builds with clang
%global toolchain clang

Name:           hiprand
Version:        %{rocm_version}
Release:        %autorelease
Summary:        HIP random number generator
Url:            https://github.com/ROCm/rocm-libraries
VCS:            git:https://github.com/ROCm/hipRAND.git
License:        MIT AND BSD-3-Clause
#!RemoteAsset:  sha256:41e4053a3c16ea4bdc6e94fff428d8ffe7279e9cfa7ec142afc50169aae2c1f8
Source:         %{url}/releases/download/rocm-%{version}/hiprand.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DCMAKE_SKIP_RPATH=ON
BuildOption(conf):  -DROCM_SYMLINK_LIBS=OFF
BuildOption(conf):  -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF
BuildOption(conf):  -DBUILD_TEST=%{build_test}

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
%if %{with test}
BuildRequires:  cmake(GTest)
%endif
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocrand)
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%description
hipRAND is a RAND marshalling library, with multiple supported backends. It
sits between the application and the backend RAND library, marshalling inputs
into the backend and results back to the application. hipRAND exports an
interface that does not require the client to change, regardless of the chosen
backend. Currently, hipRAND supports either rocRAND or cuRAND.

%package devel
Summary:        The hipRAND development package
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(rocrand)

%description devel
The hipRAND development package.

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep -a
# Remove RPATH
sed -i '/INSTALL_RPATH/d' CMakeLists.txt

# gtest requires C++14 or later
# https://github.com/ROCm/hipRAND/issues/222
sed -i -e 's@set(CMAKE_CXX_STANDARD 11)@set(CMAKE_CXX_STANDARD 14)@' \
    {,test/package/}CMakeLists.txt

%install -a
rm -f %{buildroot}%{_datadir}/doc/hiprand/LICENSE.md
rm -f %{buildroot}%{_bindir}/hipRAND/CTestTestfile.cmake

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libhiprand.so.1{,.*}

%files devel
%{_includedir}/hiprand/
%{_libdir}/cmake/hiprand/
%{_libdir}/libhiprand.so

%if %{with test}
%files test
%{_bindir}/test*
%endif

%changelog
%autochangelog
