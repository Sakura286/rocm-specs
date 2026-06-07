# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# hipFFT needs a GPU to run tests, but we could still
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

Name:           hipfft
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm FFT marshalling library
Url:            https://github.com/ROCm/rocm-libraries
VCS:            git:https://github.com/ROCm/hipFFT.git
License:        MIT
#!RemoteAsset:  sha256:f6f0352b5f9ffe53c88cea5fa40572eef0c0c1e2e50dce6f85d2c68e47afc63e
Source:         %{url}/releases/download/rocm-%{version}/hipfft.tar.gz
Patch1:         0001-hipfft-hipfftw-soversion.patch
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=%{build_test}
BuildOption(conf):  -DBUILD_CLIENTS_TESTS_OPENMP=OFF

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocfft)
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
%if %{with test}
BuildRequires:  boost-devel
BuildRequires:  cmake(GTest)
BuildRequires:  pkgconfig(fftw3)
BuildRequires:  cmake(hiprand)
BuildRequires:  cmake(rocrand)
%endif

%description
hipFFT is a FFT marshalling library. Currently, hipFFT supports either
rocFFT or cuFFT as backends. hipFFT exports an interface that does not
require the client to change, regardless of the chosen backend.

%package        devel
Summary:        The hipFFT development package
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(rocfft)

%description    devel
The hipFFT development package.

%if %{with test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{summary}
%endif

%prep -a
# CMake Error at clients/tests/CMakeLists.txt:87 (find_package):
#   No "FindHIP.cmake" found in CMAKE_MODULE_PATH.
# Remove MODULE
sed -i -e 's@find_package( HIP MODULE REQUIRED )@find_package( HIP REQUIRED )@' \
    clients/tests/CMakeLists.txt

%install -a
rm -f %{buildroot}/%{_datadir}/doc/hipfft/LICENSE.md

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libhipfft.so.0{,.*}
%{_libdir}/libhipfftw.so.0{,.*}

%files devel
%{_includedir}/hipfft/
%{_libdir}/cmake/hipfft/
%{_libdir}/libhipfft.so
%{_libdir}/libhipfftw.so

%if %{with test}
%files test
%{_bindir}/hipfft-test
%endif

%changelog
%autochangelog
