
%if 0%{?suse_version}
# 15.6
# rocm-core.x86_64: E: shlib-policy-name-error (Badness: 10000) librocm-core1
# Your package contains a single shared library but is not named after its SONAME.
%global core_name librocm-core1
%else
%global core_name rocm-core
%endif

%global upstreamname rocm-core
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

Name:           %{core_name}
Version:        %{rocm_version}
Release:        1%{?dist}
Summary:        A utility to get the ROCm release version
License:        MIT
URL:            https://github.com/ROCm/rocm-systems
Source0:        %{url}/releases/download/rocm-%{version}/%{upstreamname}.tar.gz#/%{upstreamname}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++

Provides:       rocm-core = %{version}-%{release}

ExclusiveArch:  x86_64 riscv64

%description
%{summary}

%if 0%{?suse_version}
%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig
%endif

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       rocm-core-devel = %{version}-%{release}

%description devel
%{summary}

%prep
%autosetup -p1 -n %{upstreamname}

%build
%cmake -DROCM_VERSION=%{rocm_version}
%cmake_build

%install
%cmake_install

rm -rf %{buildroot}/%{_prefix}/.info
rm -rf %{buildroot}/%{_libdir}/rocmmod
rm -rf %{buildroot}/%{_docdir}/*/LICENSE.md
rm -rf %{buildroot}/%{_libexecdir}/%{name}

mv  %{buildroot}/%{_includedir}/rocm-core/*.h %{buildroot}/%{_includedir}/
rm -rf %{buildroot}/%{_includedir}/rocm-core

find %{buildroot} -type f -name 'runpath_to_rpath.py' -exec rm {} \;

%files
%doc README.md
%license LICENSE.md
%{_libdir}/librocm-core.so.*

%files devel
%dir %{_libdir}/cmake/rocm-core
%{_includedir}/*.h
%{_libdir}/librocm-core.so
%{_libdir}/cmake/rocm-core/*.cmake

%changelog
* Mon Dec 1 2025 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Initial import from upstream (7.1.1)
