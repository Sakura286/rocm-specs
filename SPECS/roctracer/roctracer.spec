%global upstreamname roctracer
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%bcond_with compat
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

%global toolchain clang
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/')

# Needs ROCm HW and is only suitable for local testing
# GPU_TARGETS in the cmake config are only for testing
%bcond test 0

%bcond doc 0

%bcond debug 0
%if %{with debug}
%global build_type DEBUG
%else
%global build_type RelWithDebInfo
%endif

# Compression type and level for source/binary package payloads.
#  "w7T0.xzdio"	xz level 7 using %%{getncpus} threads
%define _source_payload	w7T0.xzdio
%define _binary_payload	w7T0.xzdio

Name:           roctracer%{pkg_suffix}
Version:        %{rocm_version}
Release:        1%{?dist}
Summary:        ROCm Tracer Callback/Activity Library for Performance tracing AMD GPUs

Url:            https://github.com/ROCm/%{upstreamname}
License:        MIT
Source0:        %{url}/archive/rocm-%{rocm_version}.tar.gz#/%{upstreamname}-%{rocm_version}.tar.gz

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
BuildRequires:  rocr-runtime%{pkg_suffix}-devel
#BuildRequires:  rocm-rpm-macros%{pkg_suffix}

BuildRequires:  pkgconfig(atomic_ops)
# https://github.com/ROCm/roctracer/issues/113
BuildRequires:  python3dist(cppheaderparser)

%if %{with doc}
BuildRequires:  doxygen
BuildRequires:  texlive-adjustbox
BuildRequires:  texlive-dvips
BuildRequires:  texlive-ec
BuildRequires:  texlive-hanging
BuildRequires:  texlive-latex
BuildRequires:  texlive-makeindex
BuildRequires:  texlive-metafont
BuildRequires:  texlive-multirow
BuildRequires:  texlive-newunicodechar
BuildRequires:  texlive-stackengine
BuildRequires:  texlive-texlive-scripts
BuildRequires:  texlive-tocloft
BuildRequires:  texlive-ulem
BuildRequires:  texlive-url
BuildRequires:  texlive-wasy
BuildRequires:  texlive-wasysym
%endif

ExclusiveArch:  x86_64 riscv64

%description
ROC-tracer

* ROC-tracer library: Runtimes Generic Callback/Activity APIs

  The goal of the implementation is to provide a generic independent
  from specific runtime profiler to trace API and asynchronous activity.

  The API provides functionality for registering the runtimes API
  callbacks and asynchronous activity records pool support.

* ROC-TX library: Code Annotation Events API

  Includes API for:

  * roctxMark
  * roctxRangePush
  * roctxRangePop

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%package devel
Summary:        The %{name} development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The headers of libraries for %{name}.

%if %{with doc}
%package doc
Summary:        Docs for %{name}

%description doc
%{summary}
%endif

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%autosetup -p1 -n %{upstreamname}-rocm-%{version}

# No knob in cmake to turn off testing
%if %{without test}
sed -i -e 's@add_subdirectory(test)@#add_subdirectory(test)@' CMakeLists.txt

%else

# Adjust test running script lib dir
sed -i -e 's@../lib/@../%{pkg_libdir}/@' test/run.sh

%endif

%build
%cmake \
    -DCMAKE_BUILD_TYPE=%{build_type} \
    -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang \
    -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++ \
    -DCMAKE_CXX_FLAGS="-I%{pkg_prefix}/include"\
    -DCMAKE_EXE_LINKER_FLAGS="-L %{pkg_prefix}/%{pkg_libdir} -lamdhip64" \
    -DCMAKE_INSTALL_LIBDIR=%{pkg_libdir} \
    -DCMAKE_INSTALL_PREFIX=%{pkg_prefix} \
    -DCMAKE_MODULE_PATH=%{pkg_prefix}/%{pkg_libdir}/cmake/hip \
    -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/.. \
    -DROCM_SYMLINK_LIBS=OFF \
    -DGPU_TARGETS=%{rocm_gpu_list_test} \
    -DHIP_PLATFORM=amd \
    -DHIP_HIPCC_FLAGS="-I%{pkg_prefix}/include -L%{pkg_prefix}/%{pkg_libdir} -lamdhip64" \
    -DBUILD_SHARED_LIBS=ON

%cmake_build

%if %{with doc}
%cmake_build -t doc
%endif

%install
%cmake_install

# Only install the pdf
rm -rf rm %{buildroot}%{pkg_prefix}/share/html
# Extra licenses
# Fedora
rm -f %{buildroot}%{pkg_prefix}/share/doc/*/LICENSE.md
# OpenSUSE
rm -f %{buildroot}%{pkg_prefix}/share/doc/*/*/LICENSE.md


%files
%license LICENSE.md
%doc README.md
%{pkg_prefix}/%{pkg_libdir}/libroctracer64.so.*
%{pkg_prefix}/%{pkg_libdir}/libroctx64.so.*
%{pkg_prefix}/%{pkg_libdir}/roctracer/

%files devel
%{pkg_prefix}/include/roctracer
%{pkg_prefix}/%{pkg_libdir}/libroctracer64.so
%{pkg_prefix}/%{pkg_libdir}/libroctx64.so

%if %{with doc}
%files doc
%{pkg_prefix}/share/doc/roctracer/
%endif

%if %{with test}
%files test
%{pkg_prefix}/share/roctracer/
%endif

%changelog
* Mon Jan 26 2026 Yifan Xu <xuyifan@iscas.ac.cn> -  - 7.1.1-1
- Import from upstream
