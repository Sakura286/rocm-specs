# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# rocFFT needs a GPU to run tests, but we could still
# keep the test cases for packagers who have a GPU, so make it optional.
%bcond test 1
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

Name:           rocfft
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm Fast Fourier Transforms library
Url:            https://github.com/ROCm/rocFFT
License:        MIT
#!RemoteAsset:  sha256:047e4e93e0b12869bf42136b5eb683df3a1635b01a58bbb25c8861df291ab285
Source:         %{url}/archive/rocm-%{version}.tar.gz
Patch0:         0001-cmake-use-gnu-installdirs.patch
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=%{build_test}
BuildOption(conf):  -DROCFFT_BUILD_OFFLINE_TUNER=OFF
BuildOption(conf):  -DROCFFT_KERNEL_CACHE_ENABLE=OFF
BuildOption(conf):  -DROCM_SYMLINK_LIBS=OFF
BuildOption(conf):  -DSQLITE_USE_SYSTEM_PACKAGE=ON

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  ninja
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  python3
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
%if %{with test}
BuildRequires:  cmake(GTest)
BuildRequires:  cmake(hiprand)
BuildRequires:  cmake(rocrand)
BuildRequires:  pkgconfig(fftw3)
BuildRequires:  pkgconfig(boost)
%endif

%description
rocFFT is a software library for computing fast Fourier transforms (FFTs) written
in HIP. It is part of AMD's software ecosystem based on ROCm. In addition to
AMD GPU hardware, rocFFT also works on CPU devices to facilitate testing.

%package devel
Summary:        The rocFFT development package
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(hip)

%description devel
The rocFFT development package.

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep -a
# Do not care so much about the sqlite version
sed -i -e 's@SQLite3 3.50.2 @SQLite3 @' cmake/sqlite.cmake

%install -a
# we don't need the rocfft_rtc_helper binary, don't package it
find %{buildroot} -type f -name "rocfft_rtc_helper" -print0 | xargs -0 -I {} /usr/bin/rm -rf "{}"

# we don't need or want the client-info file installed by rocfft
rm -rf %{buildroot}/%{_prefix}/.info

rm -f %{buildroot}%{_datadir}/doc/rocfft/LICENSE.md

%check
%if %{with test}
%{_vpath_builddir}/clients/staging/rocfft-test
%endif

%files
%doc README.md
%license LICENSE.md
%{_libdir}/librocfft.so.0{,.*}

%files devel
%{_includedir}/rocfft/
%{_libdir}/librocfft.so
%{_libdir}/cmake/rocfft/

%if %{with test}
%files test
%{_bindir}/rocfft-test
%{_bindir}/rtc_helper_crash
%endif

%changelog
%autochangelog
