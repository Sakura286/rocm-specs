# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%bcond test 1

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 24

Name:           hipfft
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm FFT marshalling library
URL:            https://github.com/ROCm/rocm-libraries
VCS:            git:https://github.com/ROCm/hipFFT.git
License:        MIT
#!RemoteAsset:  sha256:cd5d81b646115e38a2562174844b367afd8505390d5223192041203ceb04db98
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/hipfft.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n hipfft

BuildOption(conf):  -G Ninja
# Offload bundle IDs require an explicit host environment component.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
%ifarch riscv64
# The native GCC directory omits the GNU environment required by offload IDs.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_ARG1="--gcc-triple=%{_target_platform}"
%endif
%ifarch riscv64
BuildOption(conf):  -DCMAKE_HIP_FLAGS_INIT="--target=%{_target_cpu}-openruyi-linux-gnu --gcc-triple=%{_target_platform}"
%else
BuildOption(conf):  -DCMAKE_HIP_FLAGS_INIT="--target=%{_target_cpu}-openruyi-linux-gnu"
%endif
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=ON
BuildOption(conf):  -DBUILD_CLIENTS_TESTS_OPENMP=OFF
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  boost-devel
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(GTest)
BuildRequires:  rocm-hip-devel >= %{rocm_version}
BuildRequires:  cmake(hip)
BuildRequires:  hiprand-devel >= %{rocm_version}
BuildRequires:  cmake(hiprand)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  rocfft-devel >= %{rocm_version}
BuildRequires:  cmake(rocfft)
BuildRequires:  rocrand-devel >= %{rocm_version}
BuildRequires:  cmake(rocrand)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  pkgconfig(fftw3)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%global _description %{expand:
hipFFT is a FFT marshalling library. Currently, hipFFT supports either
rocFFT or cuFFT as backends. hipFFT exports an interface that does not
require the client to change, regardless of the chosen backend.
}

%description
%{_description}

%package        devel
Summary:        The hipFFT development package
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(rocfft)

%description    devel
The hipFFT development package.

%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}

%prep -a
# Match rocFFT: system LLVM 24 lacks the SPIR-V backend; keep native GPU targets.
sed -i '/target_.*_options(.*--offload-arch=amdgcnspirv/d' \
    clients/bench/CMakeLists.txt clients/tests/CMakeLists.txt

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH

%install -a
rm -f %{buildroot}/%{_datadir}/doc/hipfft/LICENSE.md

%if %{with test}
%check -p
export LD_LIBRARY_PATH=$PWD/%{__cmake_builddir}/library:$LD_LIBRARY_PATH
%endif

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

%files test
%{_bindir}/hipfft-test

%changelog
%autochangelog
