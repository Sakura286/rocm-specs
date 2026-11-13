# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# rocThrust's test client is HIP device-test code, need GPU to run
%bcond test 0

%global rocm_release 7.14
%global rocm_patch   1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 23

Name:           rocthrust
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm Thrust library
URL:            https://github.com/ROCm/rocThrust
# All files are Apache 2.0 with some exceptions:
# ./cmake contains only files under MIT
# ./internal/benchmark/*.py are dual licensed Apache 2.0 and Boost 1.0
# ./thrust/ contain some header files that are Boost 1.0 licensed
# ./thrust/ contain some headers that are dual Apache 2.0 and Boost 1.0
# ./thrust/cmake/FindTBB.cmake is public domain
# ./thrust/detail/allocator/allocator_traits.h is dual Apache 2.0 and MIT
# ./thrust/detail/complex contains BSD 2 clause licensed headers
License:        Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND MIT
#!RemoteAsset:  sha256:63808be10cf288fdea5ce088926e9776f0dc9a65e86bd96860308ce6ebe6338d
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-%{version}/rocthrust.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n rocthrust

BuildOption(conf):  -DROCPRIM_FETCH_METHOD=PACKAGE
BuildOption(conf):  -G Ninja
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
%if %{with test}
BuildOption(conf):  -DBUILD_TEST=ON
%endif
BuildOption(conf):  -DSQLITE_USE_SYSTEM_PACKAGE=ON
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(GTest)
BuildRequires:  cmake(hip)
BuildRequires:  rocm-hip-devel >= 7.14.1
BuildRequires:  cmake(rocprim)
BuildRequires:  rocprim-devel >= 7.14.1
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%global _description %{expand:
Thrust is a parallel algorithm library. This library has been
ported to HIP/ROCm platform, which uses the rocPRIM library.
}

%description
%{_description}

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{_description}

%if %{with test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}
%endif

%prep -a
sed -i -e 's/ROCM_INSTALL_LIBDIR lib/ROCM_INSTALL_LIBDIR %{_lib}/' cmake/ROCMExportTargetsHeaderOnly.cmake

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH

%install -a
rm -f %{buildroot}%{_docdir}/rocthrust/LICENSE

%check
%if %{with test}
%ctest
%endif

%files
%doc README.md
%license LICENSE
%license NOTICES.txt

%files devel
%{_includedir}/thrust/
%{_libdir}/cmake/rocthrust/

%if %{with test}
%files test
%{_bindir}/*.hip
%{_bindir}/test_*
%{_bindir}/rocthrust/
%endif

%changelog
%autochangelog
