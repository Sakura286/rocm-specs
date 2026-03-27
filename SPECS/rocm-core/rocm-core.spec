%global upstreamname rocm-core

%global rocm_release 7.1
%global rocm_patch 1

%global rocm_version %{rocm_release}.%{rocm_patch}
%global pkg_src rocm-%{rocm_version}

%bcond_with compat
%if %{with compat}
%global pkg_libdir lib
%global pkg_prefix %{_prefix}/lib64/rocm/rocm-%{rocm_release}/
%global pkg_suffix %{rocm_release}
%global pkg_module rocm%{pkg_suffix}
%else
%global pkg_libdir %{_lib}
%global pkg_prefix %{_prefix}
%global pkg_suffix %{nil}
%global pkg_module default
%endif

Name:           rocm-core
Version:        %{rocm_version}
Release:        %autorelease
Summary:        A utility to get the ROCm release version
License:        MIT
URL:            https://github.com/ROCm/rocm-core
Source0:        %{url}/archive/refs/tags/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOptions(conf):  -DROCM_VERSION=%{rocm_version}

BuildRequires:  cmake
BuildRequires:  gcc-c++

Provides:       rocm-core = %{version}-%{release}

%description
%{summary}

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
%{summary}

%install -a
find %{buildroot}
rm -rf %{buildroot}/%{pkg_prefix}/.info
rm -rf %{buildroot}/%{pkg_prefix}/%{pkg_libdir}/rocmmod
rm -rf %{buildroot}/%{pkg_prefix}/share/rdhc
# Extra licenses
# Fedora
rm -f %{buildroot}/%{pkg_prefix}/share/doc/*/LICENSE.md
# OpenSUSE
rm -f %{buildroot}/%{pkg_prefix}/share/doc/*/*/LICENSE.md

# Use the system include path
mv  %{buildroot}/%{pkg_prefix}/include/rocm-core/*.h %{buildroot}/%{pkg_prefix}/include/
rm -rf %{buildroot}/%{pkg_prefix}/include/rocm-core

find %{buildroot} -type f -name 'runpath_to_rpath.py' -exec rm {} \;

%files
%doc README.md
%license LICENSE.md
%{_libdir}/librocm-core.so.*
%{_bindir}/rdhc
%{_exec_prefix}/libexec/rocm-core/

%files devel
%{_includedir}/*.h
%{_libdir}/librocm-core.so
%{_libdir}/cmake/rocm-core/

%changelog
%{?autochangelog}
