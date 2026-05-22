%bcond gitcommit 0
%if %{with gitcommit}
%global commit0 2584e35062ad9c2edb68d93c464cf157bc57e3b0
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global date0 20250926
%endif

%global upstreamname hiprand
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%bcond compat 0
%if %{with compat}
%global pkg_libdir lib
%global pkg_prefix %{_prefix}/lib64/rocm/rocm-%{rocm_release}
%global pkg_suffix -%{rocm_release}
%global pkg_module rocm%{pkg_suffix}
%else
%global pkg_libdir %{_lib}
%global pkg_prefix %{_prefix}
%global pkg_suffix %{nil}
%global pkg_module default
%endif
%global hiprand_name hiprand%{pkg_suffix}

%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')

%bcond debug 0
%if %{with debug}
%global build_type DEBUG
%else
%global build_type RelWithDebInfo
%endif

%bcond test 0
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

# Option to test suite for testing on real HW:
%bcond check 0
# For docs
%bcond doc 0

# Compression type and level for source/binary package payloads.
#  "w7T0.xzdio"	xz level 7 using %%{getncpus} threads
%global _source_payload w7T0.xzdio
%global _binary_payload w7T0.xzdio

Name:           %{hiprand_name}
%if %{with gitcommit}
Version:        git%{date0}.%{shortcommit0}
Release:        3%{?dist}
%else
Version:        %{rocm_version}
Release:        1%{?dist}
%endif
Summary:        HIP random number generator
License:        MIT AND BSD-3-Clause
URL:            https://github.com/ROCm/rocm-libraries
%if %{with gitcommit}
Source0:        %{url}/archive/%{commit0}/rocm-libraries-%{shortcommit0}.tar.gz
%else
Source0:        %{url}/releases/download/rocm-%{version}/%{upstreamname}.tar.gz#/%{upstreamname}-%{version}.tar.gz
%endif

BuildRequires:  llvm
BuildRequires:  llvm-devel
BuildRequires:  clang
BuildRequires:  clang-devel
BuildRequires:  clang-tools-extra
BuildRequires:  clang-tools-extra-devel
BuildRequires:  lld
BuildRequires:  lld-devel
BuildRequires:  hipcc
BuildRequires:  compiler-rt
BuildRequires:  rocm-device-libs

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  rocm-cmake%{pkg_suffix}
BuildRequires:  rocm-comgr%{pkg_suffix}-devel
BuildRequires:  rocm-llvm%{pkg_suffix}-macros
BuildRequires:  rocm-hip%{pkg_suffix}-devel
#BuildRequires:  rocm-rpm-macros%{pkg_suffix}
BuildRequires:  rocr-runtime%{pkg_suffix}-devel
BuildRequires:  rocrand%{pkg_suffix}-devel

%if %{with test}
BuildRequires:  gtest-devel
%endif

%if %{with doc}
BuildRequires:  doxygen
%endif

Provides:       hiprand%{pkg_suffix} = %{version}-%{release}

ExclusiveArch:  x86_64 riscv64

%description
hipRAND is a RAND marshalling library, with multiple supported backends. It
sits between the application and the backend RAND library, marshalling inputs
into the backend and results back to the application. hipRAND exports an
interface that does not require the client to change, regardless of the chosen
backend. Currently, hipRAND supports either rocRAND or cuRAND.

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%package devel
Summary:        The hipRAND development package
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       rocrand%{pkg_suffix}-devel
Provides:       hiprand%{pkg_suffix}-devel = %{version}-%{release}

%description devel
The hipRAND development package.

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%if %{with gitcommit}
%setup -q -n rocm-libraries-%{commit0}
cd projects/hiprand
%else
%autosetup -p1 -n %{upstreamname}
%endif

#Remove RPATH:
sed -i '/INSTALL_RPATH/d' CMakeLists.txt

# On Tumbleweed Q2,2025
# /usr/include/gtest/internal/gtest-port.h:279:2: error: C++ versions less than C++14 are not supported.
#   279 | #error C++ versions less than C++14 are not supported.
# https://github.com/ROCm/hipRAND/issues/222
# Convert the c++11's to c++14
sed -i -e 's@set(CMAKE_CXX_STANDARD 11)@set(CMAKE_CXX_STANDARD 14)@' {,test/package/}CMakeLists.txt

%build
%if %{with gitcommit}
cd projects/hiprand
%endif

%cmake \
    -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang \
    -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++ \
    -DCMAKE_INSTALL_LIBDIR=%{pkg_libdir} \
    -DCMAKE_INSTALL_PREFIX=%{pkg_prefix} \
    -DCMAKE_LINKER=%rocmllvm_bindir/ld.lld \
    -DCMAKE_AR=%rocmllvm_bindir/llvm-ar \
    -DCMAKE_RANLIB=%rocmllvm_bindir/llvm-ranlib \
    -DCMAKE_BUILD_TYPE=%{build_type} \
    -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/.. \
    -DCMAKE_SKIP_RPATH=ON \
    -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF \
    -DAMDGPU_TARGETS=%{rocm_gpu_list_default} \
    -DBUILD_TEST=%{build_test} \
    -DROCM_SYMLINK_LIBS=OFF

%cmake_build

%install
%if %{with gitcommit}
cd projects/hiprand
%endif
%cmake_install

rm -f %{buildroot}%{pkg_prefix}/share/doc/hiprand/LICENSE.md
rm -f %{buildroot}%{pkg_prefix}/bin/hipRAND/CTestTestfile.cmake

%check
%if %{with test}
%if %{with check}

%ctest
%endif
%endif

%files
%if %{with gitcommit}
%doc projects/hiprand/README.md
%license projects/hiprand/LICENSE.md
%else
%doc README.md
%license LICENSE.md
%endif
%if %{with debug}
%{pkg_prefix}/%{pkg_libdir}/libhiprand-d.so.1{,.*}
%else
%{pkg_prefix}/%{pkg_libdir}/libhiprand.so.1{,.*}
%endif

%files devel
%{pkg_prefix}/include/hiprand/
%if %{with debug}
%{pkg_prefix}/%{pkg_libdir}/libhiprand-d.so
%else
%{pkg_prefix}/%{pkg_libdir}/libhiprand.so
%endif
%{pkg_prefix}/%{pkg_libdir}/cmake/hiprand/

%if %{with test}
%files test
%{pkg_prefix}/bin/test*
%endif

%changelog
* Mon Feb 9 2026 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
